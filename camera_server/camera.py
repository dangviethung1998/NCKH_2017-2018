import cv2
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
reg = cv2.face.LBPHFaceRecognizer_create()
reg.read('reg_data/trainedData.yml')
c = "Unknown"
font = cv2.FONT_HERSHEY_SIMPLEX
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        cvtgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
        faces = face_cascade.detectMultiScale(image, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(image	, (x,y), (x+w, y+h), (255,255,0),2)
            c, s = reg.predict(cvtgray[y:y+h, x:x+w])
            if c == 1:
				c = "Admin"
            cv2.putText(image,str(c),(x,y+h),font,1,(0,0,255))
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()