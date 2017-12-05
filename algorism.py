import time
import pigpio

pi = pigpio.pi()
if not pi.connected:
    exit()

ori = [1500,1000]
N = [0, 30]
S = [0, -30]
N2 = [0, -33]
S2 = [0, 33]
W = [-50, 0]
E = [50, 0]



limit_max_x = 1900
limit_min_x = 950

limit_min_y = 1130
limit_max_y = 1250

end_flag = 0
i = 0

arm_name = ["Camera Holder","middle","base","right","left","arm"]
arm_list = [17, 18, 27, 22, 19, 21]
arm_def_position = [2060, 970, 1500, 955, 1220, 600]
arm_cul_position = [2060, 970, 1500, 955, 1220, 600]
arm_max_position = [2060, 1250, 1900, 1160, 1130, 600]
arm_min_position = [2060, 670,  950, 600, 1250, 600]

def ctrl_direct(Motor_num, position):
    pi.set_servo_pulsewidth(Motor_num, position)
    time.sleep(0.5)
    pi.set_servo_pulsewidth(Motor_num, 0)
    time.sleep(0.2)
    
def setup():
    print("preparing...")
    for i in range(len(arm_list)):
        ctrl_direct(arm_list[i], arm_def_position[i])
    print("prepare is ready")

def speed(angle, currentval):
    val = abs(angle - currentval)
    if val > 900:
        times = 100
    elif val > 90:
        times = 10
    else:
        times = 1
    if (angle > currentval):
        step = 1*times
    else:
        step = -1*times
    return step

def move_Motor(arm_num, angle, speed):
    for i in range(arm_cul_position[arm_num], angle+speed, speed):
        pi.set_servo_pulsewidth(arm_list[arm_num], i)
        time.sleep(0.02)
    pi.set_servo_pulsewidth(arm_list[arm_num], 0)
    print(arm_name[arm_num] + " moved :" + str(arm_cul_position[arm_num]) + "->" + str(angle))

def angle_ctrl(arm_num, angle):
    global arm_cul_position
    step = speed(angle, arm_cul_position[arm_num])
    move_Motor(arm_num, angle, step)
    arm_cul_position[arm_num] = angle

def test():
    
    e_flag = 0
    n_flag = 0
    s_flag = 0
    w_flag = 0
    end_flag = 0
    i = 0
    cul_x = ori[0]
    cul_y = arm_cul_position[3]
    
    while end_flag < 1:
        
        if i%2 > 0:
            #goto East
            for j in range(i):
                cul_x = cul_x + E[0]
                if cul_x > limit_max_x:
                    cul_x = limit_max_x
                    e_flag = 1
                print("East px: " + str(cul_x) + " py: " +str(cul_y) + " flag: " + str(end_flag))
                angle_ctrl(2, cul_x)
            #goto North(Right)
            for k in range(i):
                cul_y = cul_y + N[1]
                if cul_y >= arm_max_position[3]:
                    cul_y = arm_max_position[3]
                    n_flag = 1
                print("North px: " + str(cul_x) + " py: " +str(cul_y) + " flag: " + str(end_flag))
                angle_ctrl(3, cul_y)
                angle_m = arm_cul_position[1] + N2[1]
                angle_ctrl(1,angle_m)
         
        else:
            #goto west
            for j in range(i):
                print("W" + str(j+1))
                cul_x = cul_x + W[0]
                if cul_x <= limit_min_x:
                    cul_x = limit_min_x
                    w_flag = 1
                print("px: " + str(cul_x) + " py: " +str(cul_y))
                angle_ctrl(2, cul_x)
            #goto South
            for k in range(i):
                print("S" + str(k+1))
                cul_y = cul_y + S[1]
                if cul_y <= arm_min_position[3]:
                    cul_y = arm_min_position[3]
                    s_flag = 1
                print("px: " + str(cul_x) + " py: " +str(cul_y))
                angle_ctrl(3, cul_y)
                angle_m = arm_cul_position[1] + S2[1]
                angle_ctrl(1,angle_m)
        i = i + 1
        end_flag = e_flag + w_flag + n_flag + s_flag

def test2():
    angle_ctrl(3, arm_max_position[3])
    angle_ctrl(3, arm_min_position[3])
    
setup()
test()

