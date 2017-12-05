import cv2

capture = cv2.VideoCapture(0)
capture.set(3,1920)
capture.set(4,1080)

ret, img = capture.read()

if ret == True:
    cv2.imwrite("/home/pi/test.jpg", img)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

#faces = face_cascade.detectMultiScale(gray)

#canny_img = cv2.Canny(gray,50,110)
canny_img = cv2.Canny(gray,40,60)

mu = cv2.moments(canny_img, True)

cx = int(mu["m10"]/mu["m00"])
cy = int(mu["m01"]/mu["m00"])

height = int(img.shape[0]/2)
width = int(img.shape[1]/2)

cv2.circle(img, (cx,cy), 10, (0,0,255), -1)
cv2.circle(img, (width, height), 10, (255,0,0), -1)

sx = width - cx
sy = height - cy

print("sx:{0},sy:{1}".format(sx, sy))
#print(sy)

cv2.namedWindow("img", cv2.WINDOW_NORMAL)
cv2.namedWindow("canny", cv2.WINDOW_NORMAL)

cv2.imshow("img", img)
cv2.imshow("canny", canny_img)

cv2.waitKey(0)
cv2.destroyAllWindows()
