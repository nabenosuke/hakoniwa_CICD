import mmap
import contextlib
import time
import struct
import GPy
import GPyOpt
import numpy as np
import matplotlib.pyplot as plt
print("start")

loop_num = 1
penalty_time = 60
moter_power = 15
search_num = 10
flag_maximize = True

"""
parameters = []
parameters.append([0.9, 0.9, 0.9, 0.9, 0.6, 0.6, 0.6, 0.6])
parameters.append([0.1, 0.1, 0.3, 0.3, 0.1, 0.1, 0.3, 0.3])
parameters.append([1, 0.5, 1, 0.5, 1, 0.5, 1, 0.5])
parameters.append([15, 15, 15, 15, 15, 15, 15, 15])

parameters_num = len(parameters)
test_num = len(parameters[0])
"""


base_offset = 540 + 32

result_file = open("result.txt", mode="w")


def Parameter_address(offset):
    return base_offset + offset * 4


def UnityReset():
    with open("athrill_mmap.bin", mode="r+b") as f:
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)) as m:
            m[544] = 0
            time.sleep(1)


def Unity_start():
    with open("athrill_mmap.bin", mode="r+b") as f:
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)) as m:
            m[544] = 1
            #print("unity_start")


def Unity_finish():
    with open("athrill_mmap.bin", mode="r+b") as f:
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)) as m:
            #print("Unity finish")
            m[548] = 1



def Setpara(parameter):
    with open("unity_mmap.bin", mode="r+b") as f:
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)) as m:
            string = "Set "
            for i in range(len(parameter)):
                string += str(parameter[i]) + ", "
                para_addr = Parameter_address(i)
                m[para_addr:para_addr +
                    4] = struct.pack('<f', parameter[i])
            print(string)
            result_file.writelines([string, "\n"])


def Do_test(x):
    Setpara([x[:,0], x[:,1], x[:,2], moter_power])
    #Setpara([x[:,0], 1, x[:,1],  moter_power])
    #Unity_start()
    goal_count = 0
    fail_count = 0
    goaltime_sum = 0
    while(goal_count < loop_num and fail_count < loop_num):
        Unity_start()
        time.sleep(1)
        while True:
            # wait event
            with open("unity_mmap.bin", mode="r+b") as f:
                with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)) as m:
                    event = m[560]
                    # GOAL
                    if (event == 1):
                        goal_count += 1
                        print("GOAL")
                        goaltime_byte = m[532:540]
                        goaltime_double = struct.unpack('<Q', goaltime_byte)
                        goaltime = (int(goaltime_double[0])) / 1000000
                        goaltime_sum += goaltime
                        #print("Goal time:", goaltime)
                        result_file.writelines([str(goaltime), "\n"])
                        break
                    # TIME_OVER
                    elif (event == 2):
                        fail_count += 1
                        print("Time is over")
                        break
                    # HIT_WALL
                    elif (event == 3):
                        fail_count += 1
                        print("HIT WALL")
                        break
        UnityReset()
    if (goal_count == loop_num):
        goaltime_ave = goaltime_sum / loop_num
        print("Goaltime average:", goaltime_ave, "\n")
        #result = penalty_time - goaltime_ave
        result=goaltime_ave
    else:
        print("FAILED \n")
        result_file.writelines(["FAILED \n"])
        #result = 0
        result=penalty_time
    return result

def Run_test(x):
    Setpara([x[0], x[1], x[2], moter_power])
    #Setpara([x[:,0], 1, x[:,1],  moter_power])
    #Unity_start()
    goal_count = 0
    fail_count = 0
    goaltime_sum = 0
    while(goal_count < loop_num and fail_count < loop_num):
        Unity_start()
        time.sleep(1)
        while True:
            # wait event
            with open("unity_mmap.bin", mode="r+b") as f:
                with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)) as m:
                    event = m[560]
                    # GOAL
                    if (event == 1):
                        goal_count += 1
                        print("GOAL")
                        goaltime_byte = m[532:540]
                        goaltime_double = struct.unpack('<Q', goaltime_byte)
                        goaltime = (int(goaltime_double[0])) / 1000000
                        goaltime_sum += goaltime
                        #print("Goal time:", goaltime)
                        result_file.writelines([str(goaltime), "\n"])
                        break
                    # TIME_OVER
                    elif (event == 2):
                        fail_count += 1
                        print("Time is over")
                        break
                    # HIT_WALL
                    elif (event == 3):
                        fail_count += 1
                        print("HIT WALL")
                        break
        UnityReset()
    if (goal_count == loop_num):
        goaltime_ave = goaltime_sum / loop_num
        print("Goaltime average:", goaltime_ave, "\n")
        #result = penalty_time - goaltime_ave
        result=goaltime_ave
    else:
        print("FAILED \n")
        result_file.writelines(["FAILED \n"])
        #result = 0
        result=penalty_time
    return result
init_X=[[5, 4.2, 4], [0.08, 2.8, 0.16], [4.44985774, 2.82415746, 5.], [1.74277155, 4.47926081, 2.63336341], [3.81782903, 5., 1.43780894]]
init_X_np = np.array(init_X).reshape((len(init_X[:]) , len(init_X[0])))
init_Y=[[35.14233333333333], [60], [43.626666666666665], [37.28], [39.18233333333333]]
init_Y_np = np.array(init_Y).reshape((len(init_Y) , 1))

bounds = [{'name': 'Kp', 'type': 'continuous', 'domain': (0,5)},{'name': 'Ki', 'type': 'continuous', 'domain': (0,5)}, {'name': 'Kd', 'type': 'continuous', 'domain': (0,5)}]
#bounds = [{'name': 'Kp', 'type': 'continuous', 'domain': (0,1)},{'name': 'Kd', 'type': 'continuous', 'domain': (0,1)}]

myBopt = GPyOpt.methods.BayesianOptimization(f=Do_test, X=init_X_np, Y=init_Y_np ,domain=bounds, acquisition_type='EI')
myBopt.run_optimization(max_iter=search_num)
#myBopt.Y=-1*myBopt.Y
myBopt.plot_acquisition()
myBopt.plot_convergence()

#最大化しているので結果は負の数の最小化している


Kp=myBopt.X[:,0]
Ki=myBopt.X[:,1]
Kd=myBopt.X[:,2]
result=myBopt.Y[:,0]
"""
Kp=Kp[5:]
Ki=Ki[5:]
Kd=Kd[5:]
result=result[5:]
"""
print(result)

success_index=[num for num in range(search_num) if result[num]!=penalty_time]
success_num=len(success_index)
success_x=range(success_num)
Kp_seccess = Kp[success_index]
Ki_seccess = Ki[success_index]
Kd_seccess = Kd[success_index]

fig=plt.figure()
ax1=fig.add_subplot(311, xlabel='iteration', ylabel='value of parameter')
ax1.plot(Kp, color="red", label="Kp")
ax1.plot(Ki, color="blue", label="Ki")
ax1.plot(Kd, color="green", label="Kd")
"""
ax2=fig.add_subplot(3,1,2)
ax2.plot(success_x, Kp_seccess, color="red")
ax2.plot(success_x, Ki_seccess, color="blue")
ax2.plot(success_x, Kd_seccess, color="green")
plt.xticks(success_x, success_index)
"""
ax3=fig.add_subplot(313, xlabel='iteration', ylabel='goal time')
ax3.plot(result)

plt.show()
fig.savefig("img.png")

opt_para = myBopt.x_opt
opt_para_str=str(myBopt.x_opt)
print(opt_para_str)
opt_time = penalty_time + myBopt.fx_opt
opt_time_str=str(opt_time)
print(str(myBopt.fx_opt))
print(opt_time_str)
result_str=str(myBopt.x_opt) +"  "+ str(opt_time) + "  " + str(myBopt.fx_opt)
result_file.writelines([result_str, "\n"])
result_file.close()
print("end")
Unity_finish()
time.sleep(100000)
