import mmap
import contextlib
import time
import struct
print("start")

loop_num = 3
penalty_time = 120

parameters = []
parameters.append([0.9, 0.9, 0.9, 0.9, 0.6, 0.6, 0.6, 0.6])
parameters.append([0.1, 0.1, 0.3, 0.3, 0.1, 0.1, 0.3, 0.3])
parameters.append([1, 0.5, 1, 0.5, 1, 0.5, 1, 0.5])
parameters.append([15, 15, 15, 15, 15, 15, 15, 15])
"""
parameters.append([1, 0.5, 1, 1.15, 1.5])
parameters.append([1, 0.02, 0.07, 0.09, 0.1])
parameters.append([1, 0.05, 0.1, 0.2, 0.5])
parameters.append([1, -0.01, -0.02, -0.1, -0.3])
"""
parameters_num = len(parameters)
test_num = len(parameters[0])


base_offset = 540 + 32

result_file = open("result.txt", mode="w")


def Parameter_address(offset):
    return base_offset + offset * 4


def Reset():
    with open("athrill_mmap.bin", mode="r+b") as f:
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)) as m:
            m[544] = 1
            time.sleep(1)
            m[544] = 0


def Setpara(parameter, para_index):
    with open("unity_mmap.bin", mode="r+b") as f:
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)) as m:
            string = "Set "
            for i in range(parameters_num):
                string += str(parameters[i][para_index]) + ", "
                para_addr = Parameter_address(i)
                m[para_addr:para_addr +
                    4] = struct.pack('<f', parameters[i][para_index])
            print(string)
            result_file.writelines([string, "\n"])
            """
            print("set", para)
            m[Parameter(j):Parameter(j) + 4] = struct.pack('<f', para)
            """


# リセットとパラメータ書き込みの順番
# while True:
for i in range(test_num):
    """
    Setpara(parameter1[i], 1)
    Setpara(parameter2[i], 2)
    Setpara(parameter3[i], 3)
    Setpara(parameter4[i], 4)
    Setpara(parameter5[i], 5)
    Setpara(parameter6[i], 6)
    Setpara(parameter7[i], 7)
    """
    Setpara(parameters, i)
    goal_count = 0
    goaltime_sum = 0
    for loop_count in range(loop_num):
        while True:
            # wait event
            with open("unity_mmap.bin", mode="r+b") as f:
                with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)) as m:
                    event = m[560]
                    # GOAL
                    if (event == 1):
                        print("GOAL")
                        goaltime_byte = m[532:540]
                        goaltime_double = struct.unpack('<Q', goaltime_byte)
                        goaltime = (int(goaltime_double[0])) / 1000000
                        goal_count += 1
                        goaltime_sum += goaltime
                        #print("Goal time:", goaltime)
                        result_file.writelines([str(goaltime), "\n"])
                        break
                    # TIME_OVER
                    elif (event == 2):
                        print("Time is over")
                        break
                    # HIT_WALL
                    elif (event == 3):
                        print("HIT WALL")
                        break
        Reset()
    if (goal_count > (loop_num / 3)):
        goaltime_ave = goaltime_sum / goal_count
        print("Goaltime average:", goaltime_ave, "\n")
    else:
        print("FAILED \n")

result_file.close()
print("end")
time.sleep(1000)
