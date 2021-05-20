# -*- coding: utf-8 -*-
import PyQt5, sys, mainUI, os, datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class MainWindow(QMainWindow, mainUI.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self, None)
        self.setupUi(self)

        ''' 변수 관련'''
        self.state_txt_path = ''

        ''' connect 관련 '''
        self.mask_slider.valueChanged.connect(self.mask_lcd.display)
        self.decibel_slider.valueChanged.connect(self.decibel_lcd.display)
        self.movement_slider.valueChanged.connect(self.movement_lcd.display)
        self.save_run_button.clicked.connect(self.functionSaveAndRun)


        self.state_path_Button.clicked.connect(self.state_save_select)
        self.state_reset_Button.clicked.connect(self.state_reset)
        self.event_test_button.clicked.connect(self.state_write)



    '''
    여기서부터 실행 관련 함수
    '''
    def functionSaveAndRun(self):
        self.startTimer()

        function_status = []
        if self.mask_detect.isChecked():
            function_status.append('마스크')
        if self.decibel_detect.isChecked():
            function_status.append('소음')
        if self.movement_detect.isChecked():
            function_status.append('마스크 미착용 후 이동')
        if function_status:
            self.state_function_Label.setText('/'.join(function_status) + ' 감지 활성화')
        else:
            self.state_function_Label.setText('모든 기능 비활성화')


    def startTimer(self):
        print(self.mask_slider.value())
        print(self.decibel_slider.value())
        print(self.movement_slider.value())
        print(self.mask_detect.isChecked())
        print(self.decibel_detect.isChecked())
        print(self.movement_detect.isChecked())

        self.minute_1 = self.mask_slider.value() - 1
        self.minute_2 = self.decibel_slider.value() - 1
        self.minute_3 = self.movement_slider.value() - 1

        self.second = 60

        self.myTimer = QTimer()
        self.myTimer.timeout.connect(self.timerTimeout)
        self.myTimer.start(1000)

    def timerTimeout(self):
        self.second -= 1

        if self.second == 0:
            self.second = 60
            if self.minute_1 == 0:
                self.mask_time.setText("00:00")
            if self.minute_2 == 0:
                self.decibel_time.setText("00:00")
            if self.minute_3 == 0:
                self.movement_time.setText("00:00")
            if self.minute_1 <= -1 and self.minute_2 <= -1 and self.minute_3 <= -1:
                self.myTimer.stop()
            self.minute_1 -= 1
            self.minute_2 -= 1
            self.minute_3 -= 1
        self.update_gui()

    def update_gui(self):
        if self.minute_1 >= 0 and self.mask_detect.isChecked():
            self.mask_time.setText(str(self.minute_1) + ":" + str(self.second))
        if self.minute_2 >= 0 and self.decibel_detect.isChecked():
            self.decibel_time.setText(str(self.minute_2) + ":" + str(self.second))
        if self.minute_3 >= 0 and self.movement_detect.isChecked():
            self.movement_time.setText(str(self.minute_3) + ":" + str(self.second))

    def function1(self, state):
        pass

    def function2(self, state):
        pass

    def function3(self, state):
        pass

    def state_save_select(self):
        forder_path = QFileDialog.getExistingDirectory()
        forder_path = os.path.realpath(forder_path)
        self.state_txt_path = forder_path

    def state_reset(self):
        self.state_plainTextEdit.clear()

    def state_write(self):
        now = datetime.datetime.now()
        self.state_plainTextEdit.appendPlainText(f'<{now.strftime("%Y-%m-%d %H:%M:%S")}> EventName')
        if self.state_txt_path:
            with open(f'{self.state_txt_path}/{now.strftime("%Y-%m-%d")}.txt', 'at') as state_txt_file:
                state_txt_file.write(f'<{now.strftime("%Y-%m-%d %H:%M:%S")}> EventName\n')
        else:
            with open(f'{now.strftime("%Y-%m-%d")}.txt', 'at') as state_txt_file:
                state_txt_file.write(f'<{now.strftime("%Y-%m-%d %H:%M:%S")}> EventName\n')



app =  QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec_()