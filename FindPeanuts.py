from pynput import keyboard
from pynput.keyboard import Key, Listener
import time
import pigpio
from captureTest import capture

pi = pigpio.pi()
if not pi.connected:
    exit()
#Robot Arm No.1 ~ No.6
arm_name = ["Camera Holder","middle","upper","right","left","base"]
arm_list = [17, 18, 27, 22, 19, 26]

#face search initial
arm_def_position = [2020, 520, 1400, 610, 1270, 1350]
arm_cul_position = [2020, 520, 1400, 610, 1270, 1350]

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

def searchStep(step):
    val = abs(step)
    if val > 50:
        times = 10
    else:
        times = 4
    return times


def moveOneStep(mt):
    global arm_cul_position
    for i in range(5,-1,-1):
        if mt[i] != 0 :
            angle = arm_cul_position[i] + mt[i]
            angle_ctrl(i, angle)
            

def prepare():
    maxp = [2020,720,1400,764,927,1350]
    for i in range(5,-1,-1):
        angle_ctrl(i, maxp[i])
            
#arm demo
def Test01():

    mt1 = [0,0,0,1,1,0]
    mt2 = [0,0,0,0,1,0]
    mt3 = [0,1,0,1,1,0]
    mt4 = [0,0,0,0,1,0]
    mt5 = [0,1,0,1,1,0]
    mt6 = [0,0,0,0,1,0]

    for i in range(80):
        moveOneStep(mt1)
        moveOneStep(mt2)
        moveOneStep(mt3)
        moveOneStep(mt4)
        moveOneStep(mt5)
        moveOneStep(mt6)
    
    #minp = [2020,850,1400,1010,1290,1400]
    #for i in range(5,-1,-1):
    #    angle_ctrl(i, minp[i])

    #angle_ctrl(5, 2000)

def UpDownTest():

    maxp = [2020,751,1400,830,1325,1350]
    for i in range(5,-1,-1):
        angle_ctrl(i, maxp[i])
    
    
    mt1 = [0,1,0,1,-1,0]
    mt2 = [0,1,0,1,0,0]
   

    for i in range(30):
        for j in range(9):
            moveOneStep(mt2)
        moveOneStep(mt1)
        for j in range(9):
            moveOneStep(mt2)
        

setup()
prepare()
Test01()


#base arm 
def Test02():
    
    for i in range(1000,1102,2):
        p = Test01(i)
        step = searchStep(p[0])
        print(p[0])
        print(step)
        if p[0] < 30 and p[0] > 0:
            break
        else:
            angle = arm_cul_position[5] -step            
            angle_ctrl(5, angle)
   
    print("***end***")
    
    
def OriginalPosition():
    for i in range(5,-1,-1):
        angle_ctrl(i, arm_def_position[i])
    
def print_current_position():
    for i in range(len(arm_name)):
        print(arm_name[i] + "'s current position : " + str(arm_cul_position[i]))

#hand control
def on_press(key):
    move_step = 11
    try:
        
        if key.char == "q":
            angle = arm_cul_position[0] + move_step 
            if (angle > 2370):
                angle = 2370
            angle_ctrl(0, angle)
        elif key.char == "w":
            angle = arm_cul_position[0] - move_step 
            if (angle < 500):
                angle = 500
            angle_ctrl(0, angle)
        elif key.char == "a":
            angle = arm_cul_position[1] + move_step 
            if (angle > 2500):
                angle = 2500
            angle_ctrl(1, angle)
        elif key.char == "s":
            angle = arm_cul_position[1] - move_step 
            if (angle < 500):
                angle = 500
            angle_ctrl(1, angle)
        elif key.char == "z":
            angle = arm_cul_position[2] + move_step 
            if (angle > 2500):
                angle = 2500
            angle_ctrl(2, angle)
        elif key.char == "x":
            angle = arm_cul_position[2] - move_step 
            if (angle < 500):
                angle = 500
            angle_ctrl(2, angle)
        elif key.char == "e":
            angle = arm_cul_position[3] + move_step 
            if (angle > 2500):
                angle = 2500
            angle_ctrl(3, angle)
        elif key.char == "r":
            angle = arm_cul_position[3] - move_step 
            if (angle < 500):
                angle = 500
            angle_ctrl(3, angle)
        elif key.char == "d":
            angle = arm_cul_position[4] + move_step
            if (angle > 2500):
                angle = 2500
            angle_ctrl(4, angle)
        elif key.char == "f":
            angle = arm_cul_position[4] - move_step 
            if (angle < 500):
                angle = 500
            angle_ctrl(4, angle)
        elif key.char == "c":
            angle = arm_cul_position[5] + move_step 
            if (angle > 2500):
                angle = 2500
            angle_ctrl(5, angle)
        elif key.char == "v":
            angle = arm_cul_position[5] - move_step 
            if (angle < 500):
                angle = 500
            angle_ctrl(5, angle)
        elif key.char == "p":
            print_current_position()
            
    except AttributeError:
        pass

def on_release(key):
    
    if key == keyboard.Key.esc:
        print_current_position()
        OriginalPosition()
        return False

#find Face and Move Motor
def test3():
    while True:

        #taka a capture and search a face
        cls = capture()
        rect = cls.faceThread()
        
        if rect is not None:
            w = rect[0] + int(rect[3]/2) - 160
            h = rect[1] + int(rect[3]/2) - 120
            angle_w = arm_cul_position[5] - w
            angle_h = arm_cul_position[1] - h
            for i in range(3):
                angle_ctrl(5,angle_w)
                angle_ctrl(1,angle_h)
                
def FindPeanuts():
    pass
    
        


with Listener(
    on_press = on_press,
    on_release = on_release) as listener:
    listener.join()
    
pi.stop()    
