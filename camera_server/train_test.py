import cv2
import os
import numpy as np
from PIL import Image

reg = cv2.face.LBPHFaceRecognizer_create()

path = 'facedata'

def getID(path):
	img_path = [os.path.join(path,f) for f in os.listdir(path)]
	faces = []
	IDs = []
	for impath in img_path:
		faceImg = Image.open(impath).convert('L')
		faceNP = np.array(faceImg, 'uint8')
		ID = int(os.path.split(impath)[-1].split('.')[1])
		faces.append(faceNP)
		IDs.append(ID)
		cv2.imshow("training...", faceNP)
		cv2.waitKey(10)
	return IDs, faces

Ids, faces = getID(path)
reg.train(faces, np.array(Ids))
reg.save('reg_data/trainedData.yml')
cv2.destroyAllWindows()