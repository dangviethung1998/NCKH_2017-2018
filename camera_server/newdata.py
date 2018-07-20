import cv2
import numpy as np

face_sample = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)

stt = raw_input("Nhap id: ")
c = 0

while 1:
	ret, img = cam.read()
	cvtgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	lockface = face_sample.detectMultiScale(cvtgray, 1.3, 5)
	for (x,y,w,h) in lockface:
		c += 1
		cv2.imwrite("facedata/User."+str(stt)+"."+str(c)+".jpg",cvtgray[y:y+h,x:x+w])
		cv2.rectangle(img, (x,y), (x+w, y+h), (255,255,0),2)
	cv2.imshow('running...',img)
	cv2.waitKey(1)
	if (c>30):
		break
cam.release()
cv2.destroyAllWindows()
