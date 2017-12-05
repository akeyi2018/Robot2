from pynput import keyboard
from pynput.keyboard import Key, Listener
import time
import pigpio
import os.path
import tensorflow as tf
#import tensorflow.python.platform
from captureTest import capture
from DecisionNuts import DecisionTest
from types import *

pi = pigpio.pi()
if not pi.connected:
    exit()

#set study Dictionary
cls = DecisionTest()

#Robot Arm No.1 ~ No.6
arm_name = ["Camera Holder","middle","base","right","left","arm"]
arm_list = [17, 18, 27, 22, 19, 26]

led_list = [24,20,25]

#face search initial
arm_def_position = [2000, 715, 1500, 840, 1220, 1000]
arm_cul_position = [2000, 715, 1500, 840, 1220, 1000]

for i in led_list:
    pi.set_mode(i, pigpio.OUTPUT)
    pi.set_PWM_frequency(i, 50)
    pi.set_PWM_range(i, 100)

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
        elif key.char == "t":
            findKindOfNuts()
        elif key.char == "y":
            OneCall()
            
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
    filepath = CheckPath()
    cap = capture()
    cap.StudyData(filepath)
    
    cls.GetTypeOfNuts(filepath, logits, images_placeholder, keep_prob, sess) 

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
    
setup()
#findKindOfNuts()


with Listener(
    on_press = on_press,
    on_release = on_release) as listener:
    listener.join()

for i in led_list:    
    pi.set_PWM_dutycycle(i, 0)
pi.stop()    
