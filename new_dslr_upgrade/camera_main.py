import PyQt5, sys, mainUI, os, datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import cv2
import time
import cvlib as cv
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import ImageFont, ImageDraw, Image

model = load_model('model1.h5')


class Cam_Thread(QThread):
    changePixmap = pyqtSignal(np.ndarray)

    def __init__(self, input_camera_number=0, ip='', parent=None):
        super().__init__(parent)
        self.camera_number = input_camera_number
        if(self.camera_number <10):
            self.cam = cv2.VideoCapture(self.camera_number, cv2.CAP_DSHOW)
        else:
            self.url = ip
            self.cam = cv2.VideoCapture('http://'+self.url+':4747/video')
      
        if self.cam.isOpened():
            self.connect = True
            self.running = False

    def run(self):
        while self.running and self.connect:
            self.ret, self.image = self.cam.read()
            if self.ret:  # 마스크 버튼 off일때
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                face, confidence = cv.detect_face(self.image)
                for idx, f in enumerate(face):

                    (startX, startY) = f[0], f[1]
                    (endX, endY) = f[2], f[3]

                    if 0 <= startX <= self.image.shape[1] and 0 <= endX <= self.image.shape[1] and 0 <= startY <= \
                            self.image.shape[
                                0] and 0 <= endY <= self.image.shape[0]:

                        face_region = self.image[startY:endY, startX:endX]

                        face_region1 = cv2.resize(face_region, (224, 224), interpolation=cv2.INTER_AREA)

                        x = img_to_array(face_region1)
                        x = np.expand_dims(x, axis=0)
                        x = preprocess_input(x)

                        self.prediction = model.predict(x)
                        # print('predict = ', round(prediction[0][0] * 100, 2))

                        if self.prediction < 0.7:  # 마스크 미착용으로 판별되면,
                            self.mask = False
                            cv2.rectangle(rgbImage, (startX, startY), (endX, endY), (0, 0, 255), 2)
                            Y = startY - 10 if startY - 10 > 10 else startY + 10
                            text = "No Mask ({:.2f}%)".format((1 - self.prediction[0][0]) * 100)
                            cv2.putText(rgbImage, text, (startX, Y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                        else:  # 마스크 착용으로 판별되면
                            self.mask = True
                            cv2.rectangle(rgbImage, (startX, startY), (endX, endY), (0, 255, 0), 2)
                            Y = startY - 10 if startY - 10 > 10 else startY + 10
                            text = "Mask ({:.2f}%)".format(self.prediction[0][0] * 100)
                            cv2.putText(rgbImage, text, (startX, Y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                self.changePixmap.emit(rgbImage)

                # 여기서 rgbImage는 deep_learning_detect.py 함수 통해서 rect draw

            else:
                print("no")
                self.connect = False

    def open(self):
        if self.connect:
            self.running = True

    def stop(self):
        if self.connect:
            self.running = False

    def close(self):
        if self.connect:
            self.running = False
            time.sleep(1)
            self.cam.release()
