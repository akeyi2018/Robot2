import cv2
import time
import smbus

def makeuint16(lsb,msb):
    return ((msb & 0xFF) << 8) | (lsb & 0xFF)

def readTOFSensor():

    address = 0x29
    bus = smbus.SMBus(1)

    val1 = bus.write_byte_data(address, 0x000, 0x01)
    cnt = 0
    while(cnt < 100):
        time.sleep(0.010)
        val = bus.read_byte_data(address, 0x0014)
        if (val & 0x01):
            break
        cnt += 1

    if (val & 0x01):
        data = bus.read_i2c_block_data(address, 0x14, 12)
        distance = makeuint16(data[11],data[10])
        if (distance > 0): 
            return (distance/10)
        time.sleep(66/1000000.00)
    else:
        return ("not ready")

class capture:     
    
    def faceThread(self):
        capture = cv2.VideoCapture(0)
        capture.set(3,320)
        capture.set(4,240)
        ret, img = capture.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        casecade_path = "/home/pi/opencv-3.2.0/data/haarcascades/haarcascade_frontalface_alt.xml"
        face_cascade = cv2.CascadeClassifier(casecade_path)
        faces = face_cascade.detectMultiScale(gray)
        if len(faces) > 0 :
            return faces[0]
        
    def getPeanutsWithPic2(self, num):
         
        filepath = "/home/pi/robot/test_" + str(num) + ".jpg"
        capture = cv2.VideoCapture(0)

        w = 320
        h = 240
        
        capture.set(3,w)
        capture.set(4,h)
        ret, img = capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        canny_img = cv2.Canny(gray,50,150)
        mu = cv2.moments(canny_img, True)

        height = int(h/2)
        width = int(w/2)
        
        cx = int(mu["m10"]/mu["m00"]) 
        cy = int(mu["m01"]/mu["m00"])

        sx = int((width - cx)/4)
        sy = int((height - cy)/4)
            
        p = [sx,sy]
        cv2.circle(canny_img, (width, height), 10, (255,0,0), -1)
        cv2.circle(canny_img, (cx,cy), 10, (255,255,255), -1)
        
        if ret == True:
            cv2.imwrite(filepath, canny_img)
        return p
    
    def captureTest(self, num):
        filepath = "/home/pi/robot/test" + str(num) + ".jpg"
        capture = cv2.VideoCapture(0)
        capture.set(3,1920)
        capture.set(4,1080)
        ret, img = capture.read()
        if ret == True:
            cv2.imwrite(filepath, img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        #canny_img = cv2.Canny(gray,50,110)
        canny_img = cv2.Canny(gray,50,110)

        mu = cv2.moments(canny_img, True)

        cx = int(mu["m10"]/mu["m00"])
        cy = int(mu["m01"]/mu["m00"])

        height = int(img.shape[0]/2)
        width = int(img.shape[1]/2)

        sx = width - cx
        sy = height - cy

        cv2.circle(img, (cx,cy), 10, (0,0,255), -1)
        cv2.circle(img, (width, height), 10, (255,0,0), -1)
        
        cv2.imwrite(filepath, img)
        
        p = [sx,sy]
        return p

    #black back
    def StudyData(self, filepath):
        capture = cv2.VideoCapture(0)
        w = 1280
        h = 960
        
        capture.set(3,w)
        capture.set(4,h)
        ret, img = capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        canny_img = cv2.Canny(gray,60,120)
        mu = cv2.moments(canny_img, True)

        futi = 30
        
        bx,by,bw,bh = cv2.boundingRect(canny_img)
        cv2.rectangle(img, (bx-futi,by-futi), (bx+bw+futi,by+bh+futi),(255,0,0),1)
        cv2.rectangle(img, (bx,by), (bx+bw,by+bh),(0,255,0),1)

        x = bx-futi
        y = by-futi
        width = bw+futi
        height = bh+futi
        
        src = img[y:y+height+futi,x:x+width+futi]
        
        print("width: " + str(width))
        print("height: " + str(height))

        #if width > w or height > h:
        #    print("ERROR: canot take a picture.")
        #else:
        #    cv2.imwrite(filepath, src)

        return canny_img

    def studyForWhiteHigh(self, filepath):
        #Hight: 18cm
        capture = cv2.VideoCapture(0)

        w = 1280
        h = 960
        cx = 0
        cy = 0
        capture.set(3,w)
        capture.set(4,h)
        ret, img = capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        canny_img = cv2.Canny(gray,50,80)
        mu = cv2.moments(canny_img, True)

        futi = 0
        
        bx,by,bw,bh = cv2.boundingRect(canny_img)

        if mu["m00"] > 0:
            cx = int(mu["m10"]/mu["m00"])
            cy = int(mu["m01"]/mu["m00"])

        text = "Distance:" + str(readTOFSensor())
        
        cv2.rectangle(img, (bx-futi,by-futi), (bx+bw+futi,by+bh+futi),(255,0,0),1)
        cv2.rectangle(img, (bx,by), (bx+bw,by+bh),(0,255,0),1)
        scale_text_w = "scale width: " + str(bw/80)
        scale_text_h = "scale height: " + str(bh/80)
        cv2.circle(img, (cx,cy), 5, (0,0,255))
        cv2.putText(img, text, (100,100), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
        cv2.putText(img, scale_text_w, (100,120), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
        cv2.putText(img, scale_text_h, (100,140), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))

        x = bx-futi
        y = by-futi
        width = bw+futi
        height = bh+futi
        
        src = img[y:y+height+futi,x:x+width+futi]
        
        #if width > w or height > h:
        #    print("ERROR: canot take a picture.")
        #else:
        #    cv2.imwrite(filepath, src)

        return img

    def index_emax(self, cnt):
        max_num = 0
        max_i = -1
        for i in range(len(cnt)):
            cnt_num = len(cnt[i])
            if cnt_num >max_num:
                max_num = cnt_num
                max_i = i

        return max_i

    def studyForWhiteLow(self, filepath):
        #Hight: 10cm
        capture = cv2.VideoCapture(0)

        w = 400
        h = 300
        cx = 0
        cy = 0
        capture.set(3,w)
        capture.set(4,h)
        ret, img = capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

        re, bin_cv2 = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)

        gray2 = cv2.cvtColor(bin_cv2, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray2, 25,100,3)
        mu = cv2.moments(canny)
        
        futi = 0
        
        bx,by,bw,bh = cv2.boundingRect(canny)

        if mu["m00"] > 0:
            cx = int(mu["m10"]/mu["m00"])
            cy = int(mu["m01"]/mu["m00"])

        text = "Distance:" + str(readTOFSensor())
        
        cv2.rectangle(img, (bx-futi,by-futi), (bx+bw+futi,by+bh+futi),(255,0,0),1)
        #scale_text_w = "scale width: " + str(bw/80)
        #scale_text_h = "scale height: " + str(bh/80)
        cv2.circle(img, (cx,cy), 5, (255,255,255))
        cv2.putText(img, text, (100,50), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
        #cv2.putText(img, scale_text_w, (100,120), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
        #cv2.putText(img, scale_text_h, (100,140), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))

        #x = bx-futi
        #y = by-futi
        #width = bw+futi
        #height = bh+futi
        
        #src = img[y:y+height+futi,x:x+width+futi]
        
        #if width > w or height > h:
        #    print("ERROR: canot take a picture.")
        #else:
        #    cv2.imwrite(filepath, src)

        return img

    def FindMultiObject(self):
        #Height range: 10cm-18cm
        capture = cv2.VideoCapture(0)

        w = 400
        h = 300
        cx = 0
        cy = 0
        capture.set(3,w)
        capture.set(4,h)
        ret, img = capture.read()
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

        re, bin_cv2 = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)

        gray2 = cv2.cvtColor(bin_cv2, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray2, 25,100,3)

        cnt_cont = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
        cnt_cont.sort(key = cv2.contourArea, reverse = True)

        futi = 10
        for cnt in cnt_cont:
            bx,by,bw,bh = cv2.boundingRect(cnt)
            #exclude littele rect
            if bw > 30:
                cv2.rectangle(img, (bx-futi,by-futi), (bx+bw+futi,by+bh+futi),(255,0,0),1)
            #write center circle
                cx = bx + int(bw/2)
                cy = by + int(bh/2)
                cv2.circle(img, (cx,cy), 5, (255,255,255))

        text = "Distance:" + str(readTOFSensor())
        cv2.line(img,(0,150),(400,150),(0,0,255),1)
        cv2.line(img,(200,0),(200,300),(0,0,255),1)
        cv2.putText(img, text, (10,12), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
       
        return img

    def StudyWhiteBack(self, filepath):
        #Height range: 10cm-18cm
        capture = cv2.VideoCapture(0)
        w = 400
        h = 300
        cx = 0
        cy = 0
        p = [cx,cy,0]
        capture.set(3,w)
        capture.set(4,h)
        ret, img = capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

        re, bin_cv2 = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)

        gray2 = cv2.cvtColor(bin_cv2, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray2, 25,100,3)

        cnt_cont = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
        cnt_cont.sort(key = cv2.contourArea, reverse = True)

        futi = 10
        dis = readTOFSensor()
        for cnt in cnt_cont:
            bx,by,bw,bh = cv2.boundingRect(cnt)
            #exclude littele rect
            if bw > 30:
                cv2.rectangle(img, (bx-futi,by-futi), (bx+bw+futi,by+bh+futi),(255,0,0),1)
                x = bx-futi
                y = by-futi
                width = bw+futi
                height = bh+futi
                cv2.line(img,(0,150),(400,150),(0,0,255),1)
                cv2.line(img,(200,0),(200,300),(0,0,255),1)
                #print("x=" + str(x) + "y=" + str(y))
                #print("bw=" + str(bw) + "bh=" + str(bh))
                #src = img[y:y+height+futi,x:x+width+futi]
        
                if width > w or height > h:
                    print("ERROR: canot take a picture.")
                else:
                    cv2.imwrite(filepath, img)
           
    #Update to smart Find logic 2017/08/09
    def FindSingleWhiteBack(self):
        #Height range: 10cm-18cm
        capture = cv2.VideoCapture(0)
        w = 400
        h = 300
        cx = 0
        cy = 0
        p = [cx,cy,0]
        capture.set(3,w)
        capture.set(4,h)
        ret, img = capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

        re, bin_cv2 = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)

        gray2 = cv2.cvtColor(bin_cv2, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray2, 25,100,3)

        cnt_cont = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
        cnt_cont.sort(key = cv2.contourArea, reverse = True)

        futi = 10
        min_x = w
        min_y = h
        max_w = 0
        max_h = 0
        dis = readTOFSensor()
        for cnt in cnt_cont:
            bx,by,bw,bh = cv2.boundingRect(cnt)
            #exclude littele rect
            if bw > 30 and bh > 30:
                if bx < min_x:
                    min_x = bx
                if by < min_y:
                    min_y = by
                if bw > max_w:
                    max_w = bw
                if bh > max_h:
                    max_h = bh
                    
        cx = min_x + int(max_w/2)
        cy = min_y + int(max_h/2)       
        px = cx - int(w/2)
        py = cy - int(h/2)

        if max_w == 0 and max_h == 0:
            p = [px, py, 0]
        else:
            p = [px, py, dis]
                      
        return p

    def ObjectSmartFind(self):
        #Height range: 10cm-18cm
        capture = cv2.VideoCapture(0)

        w = 400
        h = 300
        cx = 0
        cy = 0
        capture.set(3,w)
        capture.set(4,h)
        ret, img = capture.read()
        #Binary process
        re, bin_cv = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)
        #make it gray
        gray = cv2.cvtColor(bin_cv, cv2.COLOR_BGR2GRAY)
        #Find Edge
        canny = cv2.Canny(gray, 25,100,3)

        cnt_cont = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
        cnt_cont.sort(key = cv2.contourArea, reverse = True)

        futi = 10
        min_x = w
        min_y = h
        max_w = 0
        max_h = 0
        for cnt in cnt_cont:
            
            bx,by,bw,bh = cv2.boundingRect(cnt)
            #exclude littele rect
            if bw > 50 and bh > 50:
                if bx < min_x:
                    min_x = bx
                if by < min_y:
                    min_y = by
                if bw > max_w:
                    max_w = bw
                if bh > max_h:
                    max_h = bh
           
        
        #cv2.rectangle(img, (min_x-futi,min_y-futi), (min_x+max_w+futi,min_y+max_h+futi),(255,0,0),1)
            #write center circle
        cx = min_x + int(max_w/2)
        cy = min_y + int(max_h/2)
        px = cx - int(w/2)
        py = cy - int(h/2)
        #scale_text_w = "scale width: " + str(max_w/50)
        #scale_text_h = "scale height: " + str(max_h/50)
        scale_text_w = "x: " + str(px)
        scale_text_h = "y: " + str(py)
        cv2.circle(img, (cx,cy), 5, (255,255,255))
        
        text = "Distance:" + str(readTOFSensor())
        cv2.line(img,(0,150),(400,150),(0,0,255),1)
        cv2.line(img,(200,0),(200,300),(0,0,255),1)
        cv2.putText(img, text, (10,12), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
        cv2.putText(img, scale_text_w, (10,30), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))
        cv2.putText(img, scale_text_h, (10,45), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,0))

        return img,cx,cy

    def cal_base(self,rect_list_x):
        g1 = []
        g2 = []
        temp1 = rect_list_x[0]
        print(rect_list_x)
        for x in rect_list_x:
            if abs(x - temp1) < 50:
                g1.insert(0,x)
            else:
                g2.insert(0,x)

        base_value = []
        if len(g1) > len(g2):
            base_value = g1
        else:
            base_value = g2
            
        return base_value
        
    def get_base_value(self):
        
        a = capture()
        rect_list_x = []
        rect_list_y = []

        for i in range(10):
            img,cx,cy = a.ObjectSmartFind()
            rect_list_x.insert(0,cx)
            rect_list_y.insert(0,cy)
          
        base_x = a.cal_base(rect_list_x)
        base_y = a.cal_base(rect_list_y)
        
        return base_x,base_y

if __name__ == "__main__":
   
    while True:
    #a.StudyWhiteBack("/home/pi/robot/test_img.jpg")
        a = capture()
        img,cx,cy = a.ObjectSmartFind()
        cv2.imshow("ret", img)
        time.sleep(0.1)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
            
    cv2.destroyAllWindows()

