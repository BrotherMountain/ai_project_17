import PyQt5, sys, mainUI, os, datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import cv2
import time


class Cam_Thread(QThread):
    changePixmap = pyqtSignal(np.ndarray)

    def __init__(self, _mask, parent=None):
        super().__init__(parent)
        self.bMask = _mask
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if self.cam.isOpened():
            self.connect = True
            self.running = False

    def run(self):
        print("영상 클래스 상태", self.bMask)
        while self.running and self.connect:
            self.ret, self.image = self.cam.read()
            if self.ret and (self.bMask is False):  # 마스크 버튼 off일때
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.changePixmap.emit(rgbImage)

            # elif self.ret and (self.bMask is True):
            #     print("영상 클래스 상태", self.bMask)
            #     if not self.ret:
            #         print("Could not read frame")
            #         exit()
            #
            #     # apply face detection
            #     face, confidence = cv.detect_face(self.image)
            #
            #     # loop through detected faces
            #     for idx, f in enumerate(face):
            #
            #         (startX, startY) = f[0], f[1]
            #         (endX, endY) = f[2], f[3]
            #
            #         if 0 <= startX <= self.image.shape[1] and 0 <= endX <= self.image.shape[1] and 0 <= startY <= self.image.shape[
            #             0] and 0 <= endY <= self.image.shape[0]:
            #
            #             face_region = self.image[startY:endY, startX:endX]
            #
            #             face_region1 = cv2.resize(face_region, (224, 224), interpolation=cv2.INTER_AREA)
            #
            #             x = img_to_array(face_region1)
            #             x = np.expand_dims(x, axis=0)
            #             x = preprocess_input(x)
            #
            #             prediction = model.predict(x)
            #             print('predict = ', round(prediction[0][0] * 100, 2))
            #
            #             if prediction < 0.7:  # 마스크 미착용으로 판별되면,
            #                 cv2.rectangle(self.image, (startX, startY), (endX, endY), (0, 0, 255), 2)
            #                 Y = startY - 10 if startY - 10 > 10 else startY + 10
            #                 text = "No Mask ({:.2f}%)".format((1 - prediction[0][0]) * 100)
            #                 cv2.putText(self.image, text, (startX, Y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            #
            #             else:  # 마스크 착용으로 판별되면
            #                 cv2.rectangle(self.image, (startX, startY), (endX, endY), (0, 255, 0), 2)
            #                 Y = startY - 10 if startY - 10 > 10 else startY + 10
            #                 text = "Mask ({:.2f}%)".format(prediction[0][0] * 100)
            #                 cv2.putText(self.image, text, (startX, Y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            #
            #     # display output
            #     rgbImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            #     self.changePixmap.emit(rgbImage)

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
