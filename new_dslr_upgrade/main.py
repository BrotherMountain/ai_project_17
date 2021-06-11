# -*- coding: utf-8 -*-
import PyQt5, sys, mainUI, os, datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import cv2
import time
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
import threading

import camera_main

class MainWindow(QMainWindow, mainUI.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self, None)
        self.bMask = False
        self.setupUi(self)

        '''웹캠 연결 버튼(숨기기)'''
        self.webcam.hide()
        self.phone.hide()
        self.DSLR.hide()

        ''' 변수 관련'''
        self.state_txt_path = ''
        self.cnt_3 = 0 # 주어진 시간동안 음성 출력 1번 제한
        self.function1_thread = threading.Timer(1, self.function1)
        self.function2_thread = threading.Timer(1, self.function2)
        self.function3_thread = threading.Timer(1, self.function3)


        ''' connect 관련 '''
        self.camera_on.clicked.connect(self.select_cam)
        self.camera_off.clicked.connect(self.camera_offline)
        self.webcam.clicked.connect(self.WebCam_activate)
        self.phone.clicked.connect(self.phone_activate)
        self.DSLR.clicked.connect(self.DSLR_activate)

        self.mask_slider.valueChanged.connect(self.mask_lcd.display)
        self.decibel_slider.valueChanged.connect(self.decibel_lcd.display)
        self.movement_slider.valueChanged.connect(self.movement_lcd.display)
        self.save_run_button.clicked.connect(self.functionSaveAndRun)

        self.state_path_Button.clicked.connect(self.state_save_select)
        self.state_reset_Button.clicked.connect(self.state_reset)

    '''
    여기서부터 실행 관련 함수
    '''

    def setImage(self, image):
        h, w, ch = image.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(image.data, w, h, bytesPerLine, QImage.Format_RGB888)
        qimg = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        # self.camera.setScaledContents(True)
        self.camera.setPixmap(QPixmap.fromImage(qimg))

    def WebCam_activate(self):
        camera_number = 0              #후에 외부 웹캠 연결시 -1번으로 설정
        self.CAM = camera_main.Cam_Thread(camera_number)
        if self.CAM.connect:
            print("connect")
            self.CAM.changePixmap.connect(self.setImage)
            self.camera_online()        # 카메라 연결 온라인
        else:
            print("not connect")

    def phone_activate(self):
        camera_number = 10            # 카메라 연결 번호는 str형태이므로 임의로 10번을 주었다.
        my_ip = '172.18.11.13'        # droidcam앱의 port 번호를 적어주세요. 마지막 4747을 제외하고 적어주세요
        self.CAM = camera_main.Cam_Thread(camera_number, my_ip)
        if self.CAM.connect:
            print("connect")
            self.CAM.changePixmap.connect(self.setImage)
            self.camera_online()        # 카메라 연결 온라인
        else:
            print("not connect")

    def DSLR_activate(self):
        camera_number = 1       # 카메라 연결번호
        self.CAM = camera_main.Cam_Thread(camera_number)
        if self.CAM.connect:
            print("connect")
            self.CAM.changePixmap.connect(self.setImage)
            self.camera_online()        # 카메라 연결 온라인
        else:
            print("not connect")

    def select_cam(self):
        self.webcam.show()
        self.phone.show()
        self.DSLR.show()


    def camera_online(self):
        self.webcam.hide()
        self.phone.hide()
        self.DSLR.hide()
        if self.CAM.connect:
            self.CAM.open()
            self.CAM.start()
            self.camera_on.setEnabled(False)
            self.camera_off.setEnabled(True)

    def camera_offline(self):
        if self.CAM.running:
            self.CAM.close()
            self.CAM.terminate()
        QApplication.closeAllWindows()

    """ 저장및 실행버튼을 누를경우 작동 """

    def functionSaveAndRun(self):
        self.cnt_3 = 0
        self.startTimer()

        function_status = []
        if self.mask_detect.isChecked():
            function_status.append('마스크')
            self.function1_thread.start()

        else:
            self.function1_thread.cancel()

        if self.decibel_detect.isChecked():
            function_status.append('소음')
        else:
            self.function2_thread.cancel()

        if self.movement_detect.isChecked():
            function_status.append('마스크 미착용 후 이동')
            self.function1_thread.start()

        else:
            self.function3_thread.cancel()

            
        if function_status:
            self.state_function_Label.setText('/'.join(function_status) + ' 감지 활성화')
        else:
            self.state_function_Label.setText('모든 기능 비활성화')

    def startTimer(self):
        print("\nmask_slider", self.mask_slider.value())
        print("decibel_slider", self.decibel_slider.value())
        print("movement_slider", self.movement_slider.value())
        print("mask_detect", self.mask_detect.isChecked())
        print("decibel_detect", self.decibel_detect.isChecked())
        print("movement_detect", self.movement_detect.isChecked())

        self.minute_1 = (self.mask_slider.value() - 1)
        self.minute_2 = self.decibel_slider.value() - 1
        self.minute_3 = self.movement_slider.value() - 1

        self.second_1 = 60
        self.second_2 = 60
        self.second_3 = 60

        self.myTimer = QTimer()
        self.myTimer.timeout.connect(self.timerTimeout)
        self.myTimer.start(1000)

    def timerTimeout(self):
        # if self.start_mask:
        self.second_1 -= 1
        if self.second_1 == 0:
            self.second_1 = 60
            if self.minute_1 == 0:
                self.mask_time.setText("00:00")
            self.minute_1 -= 1

        self.second_2 -= 1
        if self.second_2 == 0:
            self.second_2 = 60
            if self.minute_2 == 0:
                self.decibel_time.setText("00:00")
            self.minute_2 -= 1

        self.second_3 -= 1
        if self.second_3 == 0:
            self.second_3 = 60
            if self.minute_3 == 0:
                self.movement_time.setText("00:00")
                self.cnt_3 = 0
            self.minute_3 -= 1

        if self.minute_1 <= -1 and self.minute_2 <= -1 and self.minute_3 <= -1:
            # self.myTimer.stop()
            self.startTimer()

        self.update_gui()

    def update_gui(self):
        if self.minute_1 >= 0 and self.mask_detect.isChecked() and self.start_mask:
            self.mask_time.setText(str(self.minute_1) + ":" + str(self.second_1))
        if self.minute_2 >= 0 and self.decibel_detect.isChecked():
            self.decibel_time.setText(str(self.minute_2) + ":" + str(self.second_2))
        if self.minute_3 >= 0 and self.movement_detect.isChecked():
            self.movement_time.setText(str(self.minute_3) + ":" + str(self.second_3))

    def function1(self):
        try:
            if self.CAM.running:
                mask = self.CAM.mask

                if mask:
                    print("마스크를 착용하고 있습니다.")
                    self.start_mask = False
                else:
                    print("마스크를 착용하지 않고 있습니다.")
                    self.state_write('마스크 미착용')
                    self.start_mask = True
        except:
            print("function1 작동 실패")
            pass

    def function2(self, state):
        pass

    count = 0
    x = []
    y = []
    def function3(self):
        try:
            # print("초 단위", self.second_2)
            if self.CAM.running:
                self.count += 1

                # 새로운 좌표값을 받기 위해 초기화
                if self.count == 3:
                    self.count = 1
                    self.x.clear()
                    self.y.clear()

                # print("count", self.count)
                print("main x, y: ", self.CAM.startX, self.CAM.startY) #좌표값 확인
                self.x.append(self.CAM.startX)
                self.y.append(self.CAM.startY)

                # 두 개의 좌표 입력받으면 속도 구함
                if self.count == 2:
                    x_2 = (self.x[0] - self.x[1]) * (self.x[0] - self.x[1])
                    y_2 = (self.y[0] - self.y[1]) * (self.y[0] - self.y[1])

                    dis = math.sqrt(x_2 + y_2)
                    v = dis  # 프레임을 읽을 때마다 1초씩 걸린다. t=1
                    print("v: ", v)
                    if v > 150 and self.cnt_3 == 0:
                        playsound.playsound("no_run.mp3")
                        self.state_write('마스크 미착용 후 이동 감지')
                        self.cnt_3 += 1
        except:
            print("function3 작동 실패")
            pass

    def state_save_select(self):
        forder_path = QFileDialog.getExistingDirectory()
        forder_path = os.path.realpath(forder_path)
        self.state_txt_path = forder_path

    def state_reset(self):
        self.state_plainTextEdit.clear()

    def state_write(self, event_name):
        now = datetime.datetime.now()
        self.state_plainTextEdit.appendPlainText(f'<{now.strftime("%Y-%m-%d %H:%M:%S")}> {event_name}')
        if self.state_txt_path:
            with open(f'{self.state_txt_path}/{now.strftime("%Y-%m-%d")}.txt', 'at') as state_txt_file:
                state_txt_file.write(f'<{now.strftime("%Y-%m-%d %H:%M:%S")}> {event_name}\n')
        else:
            with open(f'{now.strftime("%Y-%m-%d")}.txt', 'at') as state_txt_file:
                state_txt_file.write(f'<{now.strftime("%Y-%m-%d %H:%M:%S")}> {event_name}\n')


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec_()
