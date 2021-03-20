# hakoniwa_CICD

ev3rt-athrill-v850e2m/sdk/workspace/ にline_trace_CICDを配置し、アプリケーションフォルダとしてビルドする
Unityのシミュレータを起動し、line_trace_CICDフォルダでpython3 Bayes_test.pyを実行することで、パラメータ探索が始まる

Bayes_test.py
  テスト制御モジュール
  ベイズ最適化によってパラメータ探索を行う
  
app.c
  ロボット制御パラメータ
  実行時に制御パラメータ、Kp、Ki、Kd、MOTOR_POWERを読み込む。(MOTOR_POWERは固定値)
  
