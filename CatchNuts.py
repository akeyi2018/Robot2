from pynput import keyboard
from pynput.keyboard import Key, Listener
import time
import pigpio
import os.path
import tensorflow as tf
import cv2
from captureTest import capture
from DecisionNuts import DecisionTest
from types import *

pi = pigpio.pi()
if not pi.connected:
    exit()

#set study Dictionary
cls = DecisionTest()

def findKindOfNuts():
    
    IMAGE_SIZE = 56
    IMAGE_PIXELS = IMAGE_SIZE*IMAGE_SIZE*3

    global images_placeholder,keep_prob,logits,sess,saver
    
    images_placeholder = tf.placeholder("float", shape=(None, IMAGE_PIXELS))
    keep_prob = tf.placeholder("float")
    logits = cls.inference(images_placeholder, keep_prob)
    
    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())
    
    saver = tf.train.Saver()
    saver.restore(sess, "./models/model.ckpt")

    print(logits)
    print(images_placeholder)
    print(keep_prob)


findKindOfNuts()

#Robot Arm No.1 ~ No.6
arm_name = ["Camera Holder","middle","base","right","left","arm"]
arm_list = [17, 18, 27, 22, 19, 21]

led_list = [24,20,25]

#face search initial
arm_def_position = [2290, 790, 1500, 680, 1430, 1000]
arm_cul_position = [2290, 790, 1500, 680, 1430, 1000]
arm_max_position = [2290, 1250, 1900, 1160, 1430, 600]
arm_min_position = [2290, 670,  950, 680, 750, 600]

def ctrl_direct(Motor_num, position):
    pi.set_servo_pulsewidth(Motor_num, position)
    time.sleep(0.5)
    pi.set_servo_pulsewidth(Motor_num, 0)
    time.sleep(0.2)

def setup():
    print("preparing...")
    for i in range(len(arm_list)):
        ctrl_direct(arm_list[i], arm_def_position[i])
    for i in led_list:    
        pi.set_PWM_dutycycle(i, 100)
    print("prepare is ready")
    

def speed(angle, currentval):
    val = abs(angle - currentval)
    if val > 200:
        times = 30
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
    #print(arm_name[arm_num] + " moved :" + str(arm_cul_position[arm_num]) + "->" + str(angle))

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

def closeArm():
    angle_ctrl(5, 2000)

def openArm():
    angle_ctrl(5, 1000)

def upLeft():
    angle_ctrl(4,1250)

def downLeft():
    angle_ctrl(4,1130)

def trunRight60():
    angle_ctrl(2,800)
    
def trunMiddle():
    angle_ctrl(2,1500)
    
def trunLeft60():
    angle_ctrl(2,1900)

def moveOneStep(mt):
    global arm_cul_position
    for i in range(5,-1,-1):
        if mt[i] != 0 :
            angle = arm_cul_position[i] + mt[i]
            for j in range(2):
                angle_ctrl(i, angle)
            
def OriginalPosition():
    for i in range(5,-1,-1):
        angle_ctrl(i, arm_def_position[i])
    
def print_current_position():
    for i in range(len(arm_name)):
        print(arm_name[i] + "'s current position : " + str(arm_cul_position[i]))

#hand control
def on_press(key):
    move_step = 5
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
            trunRight60()
        elif key.char == "x":
            trunMiddle()
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
            #upLeft()
        elif key.char == "f":
            angle = arm_cul_position[4] - move_step 
            if (angle < 500):
                angle = 500
            angle_ctrl(4, angle)
            #downLeft()
        elif key.char == "b":
            closeArm()
        elif key.char == "v":
            openArm()
        elif key.char == "p":
            print_current_position()
        elif key.char == "t":
            GetNutsPosition()
        elif key.char == "y":
            OneCall()
        elif key.char == "o":
            OriginalPosition()
        elif key.char == "m":
            trunLeft60()
            
    except AttributeError:
        pass

def on_release(key):
    
    if key == keyboard.Key.esc:
        print_current_position()
        OriginalPosition()
        return False

def CheckPath():
    path = "/home/pi/robot/pic/t_"
    for i in range(1000,9999,1):
        tmp = path + str(i) + ".jpg"
        if os.path.exists(tmp) == True:
            pass
        else:
            return tmp

def rollhead():
    global arm_cul_position
    rollband = -33
    for i in range(10):
        filepath = CheckPath()
        cap = capture()
        cap.StudyData(filepath)
        clockwise = arm_cul_position[0] + rollband
        angle_ctrl(0, clockwise)
        time.sleep(0.5)
    OriginalPosition()

def OneCall():
    #filepath = CheckPath()
    cap = capture()
    img = cap.FindMultiObject()
    cls.GetTypeOfNuts(img, logits, images_placeholder, keep_prob, sess) 

def UzumakiSearch():
 
    e_flag = 0
    n_flag = 0
    s_flag = 0
    w_flag = 0
    end_flag = 0
    i = 0
    
    N = [0, 30]
    S = [0, -30]
    N2 = [0, -33]
    S2 = [0, 33]
    W = [-50, 0]
    E = [50, 0]

    cul_x = arm_cul_position[2]
    cul_y = arm_cul_position[3]
    
    while end_flag < 1:

        if i%2 > 0:
            #goto East
            for j in range(i):
                cul_x = cul_x + E[0]
                if cul_x >= arm_max_position[2]:
                    cul_x = arm_max_position[2]
                    e_flag = 1
                #print("East px: " + str(cul_x) + " py: " +str(cul_y) + " flag: " + str(end_flag))
                for ct in range(2):
                    angle_ctrl(2, cul_x)
                if GotNuts() == True:
                    end_flag = 2
                    break
                
            #goto North(Right)
            for k in range(i):
                cul_y = cul_y + N[1]
                if cul_y >= arm_max_position[3]:
                    cul_y = arm_max_position[3]
                    n_flag = 1
                #print("North px: " + str(cul_x) + " py: " +str(cul_y) + " flag: " + str(end_flag))
                for ct in range(2):
                    angle_ctrl(3, cul_y)
                angle_m = arm_cul_position[1] + N2[1]
                for ct in range(2):
                    angle_ctrl(1,angle_m)
                if GotNuts() == True:
                    end_flag = 2
                    break
        else:
            #goto west
            for j in range(i):
                print("W" + str(j+1))
                cul_x = cul_x + W[0]
                if cul_x <= arm_min_position[2]:
                    cul_x = arm_min_position[2]
                #print("px: " + str(cul_x) + " py: " +str(cul_y))
                for ct in range(2):
                    angle_ctrl(2, cul_x)
                if GotNuts() == True:
                    end_flag = 2
                    break
            #goto South
            for k in range(i):
                print("S" + str(k+1))
                cul_y = cul_y + S[1]
                if cul_y <= arm_min_position[3]:
                    cul_y = arm_min_position[3]
                #print("px: " + str(cul_x) + " py: " +str(cul_y))
                for ct in range(2):
                    angle_ctrl(3, cul_y)
                angle_m = arm_cul_position[1] + S2[1]
                for ct in range(2):
                    angle_ctrl(1,angle_m)
                if GotNuts() == True:
                    end_flag = 2
                    break
        i = i + 1

def GotNuts():
    cap = capture()
    p = cap.FindSingleWhiteBack()
    #Not Found Object
    print(p)
    if p[2] == 0:
        return False
    else:
        return True

def MoveToTarget():
    global arm_cul_position
    gosa = 20
    cap = capture()
    p = [100,100,10]
    while (abs(p[0]) >= gosa) or (abs(p[1]) >= gosa):
        p = cap.FindSingleWhiteBack()
        angle_w = arm_cul_position[2] - p[1]
        for i in range(2):
            angle_ctrl(2,angle_w)
        
        angle_h = arm_cul_position[3] - int(p[0]/2)
        for i in range(2):
            angle_ctrl(3,angle_h)

    #print(p)
    return 1
        
def GetNutsPosition():
    
    OriginalPosition()
    UzumakiSearch()
    print("Uzumaki end")
    
    flg = MoveToTarget()
    
    if flg == 1:
        print("Catched target")
    else:
        print("Not found object")

    #goto catch
    gotoCatchPosition()

    catchAndGo()

def UpArmByLeft(cls):
    print("move left servo")
    low_limit = 6.2
    while True:
        p = cls.FindSingleWhiteBack()
        print(p)
        if p[2] < low_limit:
            #print("move left servo")
            angle_left = arm_cul_position[4] + 5
            #angle_m = arm_cul_position[3] - 5
            angle_ctrl(4, angle_left)
            #angle_ctrl(3, angle_m)
        else:
            break

def gotoCatchPosition():
    global arm_cul_position
    downLeft()
    distance_high_limit = 6.8
    distance_low_limit = 6.2    
    x_position_lmt = 25
    y_position_lmt = 25
    cap = capture()
    p = [100,100,10]
    while (abs(p[0]) >= x_position_lmt) or (abs(p[1]) >= y_position_lmt) or (abs(p[2]) >= distance_high_limit):
        p = cap.FindSingleWhiteBack()

        if p[2] > 7:
            angle_right = arm_cul_position[3] + 15
            angle_m = arm_cul_position[1] + 16
            angle_ctrl(3, angle_right)
            angle_ctrl(1, angle_m)
        elif p[2] > 6.6:
            angle_right = arm_cul_position[3] + 5
            angle_m = arm_cul_position[1] + 6
            angle_ctrl(3, angle_right)
            angle_ctrl(1, angle_m)
        #elif p[2] ==0:
        #    print(p)
        #    break
        else:
            pass
        
        #Base Position
        angle_base = arm_cul_position[2] - p[1]
        for i in range(3):
            angle_ctrl(2, angle_base)
        #Right Position
        if arm_cul_position[3] > 1300:
            angle_right = arm_cul_position[3] + int(p[0]/2)
            angle_left = arm_cul_position[4] + 5
        else:
            angle_right = arm_cul_position[3] - int(p[0]/2)
            angle_left = arm_cul_position[4] - 5

        for i in range(3):
            angle_ctrl(3, angle_right)
            angle_ctrl(4, angle_left)
            
        #distance Position
        if p[2] < distance_low_limit:
            UpArmByLeft(cap)
        print(p)
    print("end of arm")
    
def gotoPosition():

    global arm_cul_position
    
    hight_limit = 6.4
    low_limit = 6.4
        
    cls = capture()
    lmt = 15
    downLeft()
    
    while True:
        
        p = cls.FindSingleWhiteBack()

        if p[2] == hight_limit:
            break
        #over low limit case
        elif p[2] < low_limit:
            UpArmByLeft(cls)
       
        if p[2] > 7:
            
            angle_right = arm_cul_position[3] + 50
            angle_m = arm_cul_position[1] + 60
            angle_ctrl(3, angle_right)
            angle_ctrl(1, angle_m)
        else:
            angle_right = arm_cul_position[3] + 10
            angle_m = arm_cul_position[1] + 13
            angle_ctrl(3, angle_right)
            angle_ctrl(1, angle_m)
        
        if p[2] <= 6.7:
            lmt = 12
        time.sleep(0.2)
        while True:
            time.sleep(0.2)
            p2 = cls.FindSingleWhiteBack()
            print(p2)
            if abs(p2[1]) > lmt:
                angle_base = arm_cul_position[2] - p2[1]
                for i in range(3):
                    angle_ctrl(2, angle_base)

            if abs(p2[0]) > lmt:

                if arm_cul_position[3] > 1300:
                    angle_right = arm_cul_position[3] + int(p2[0]/2)
                else:
                    angle_right = arm_cul_position[3] - int(p2[0]/2)
                
                for i in range(3):
                    angle_ctrl(3, angle_right)
            
            if abs(p2[0]) <= lmt and abs(p2[1]) <= lmt:
                break
            
        #filepath = CheckPath()
        #cls.StudyWhiteBack(filepath)
        catchAndGo()
        break

def catchAndGo():

    closeArm()
    time.sleep(0.5)
    upRightArm()
    trunRight60()
    openArm()

def upRightArm():
    angle_ctrl(3,700)
    
setup()


with Listener(
    on_press = on_press,
    on_release = on_release) as listener:
    listener.join()

#for i in led_list:    
#    pi.set_PWM_dutycycle(i, 0)

pi.stop()    
