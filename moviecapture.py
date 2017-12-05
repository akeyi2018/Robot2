import cv2
import time
import threading

cap = cv2.VideoCapture(0)
cap.set(3,320)
cap.set(4,240)

def faceThread(img):
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    casecade_path = "/home/pi/opencv-3.2.0/data/haarcascades/haarcascade_frontalface_alt_tree.xml"
    face_cascade = cv2.CascadeClassifier(casecade_path)
    faces = face_cascade.detectMultiScale(gray)
    color = (255,0,255)
    
    if len(faces) > 0 :
        for rect in faces:
            #print(rect[0:2])
            #print(rect[2:4])
            #for i in rect:
            #    print(i)
            w = rect[0] + int(rect[3]/2)
            h = rect[1] + int(rect[3]/2)
            #cv2.rectangle(img, tuple(rect[0:2]), tuple(rect[0:2]+rect[2:4]), color, thickness =2)
            #cv2.circle(img, (w,h), 10, (255,0,0), -1)
        #cv2.imwrite("/home/pi/robot/detected.jpg", img)
        #return img
        return w

def showFace():
    while True:
        ret, frame = cap.read()
        #cv2.imshow("camera capture",frame)
        #if(threading.active_count() == 1):qqq
        #tmp = faceThread(frame)
        
        cv2.imshow("camera capture",frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

def Test():
    ret, frame = cap.read()
       
    faceThread(frame)
    cv2.imshow("camera capture",frame)
        
    if cv2.waitKey(1) & 0xFF == ord("q"):
        exit()

showFace()
cap.release()
cv2.destroyAllWindows()

