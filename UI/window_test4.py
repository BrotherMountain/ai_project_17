# test
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QCheckBox, QLCDNumber, QGridLayout, QGroupBox, \
    QVBoxLayout, QHBoxLayout, QSlider
from PyQt5.QtCore import Qt
import cv2
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QPixmap

# 123123
class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while True:
            ret, frame = self.cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.state_label()
        # self.slider()
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        grid = QGridLayout()
        grid.addWidget(self.camera_line(), 0, 0, 3, 2)
        grid.addWidget(self.checkbox(), 0, 2, 3, 1)
        grid.addWidget(self.waiting_time(), 3, 2, 1, 1)
        grid.addWidget(self.state_line(), 3, 0, 1, 2)
        self.setLayout(grid)

        self.setWindowTitle('test')
        self.setGeometry(50, 50, 1200, 800)
        # setGeometry(프로그램과 모니터 왼쪽 거리, 프로그램과 모니터 위쪽 거리, 프로그램 가로 길이, 프로그램 세로 길이)
        self.show()

    def state_label(self):
        # 체크 박스 클릭했을 때 뜨는 확인문구들
        self.fun_lbl1 = QLabel(" " * 80, self)
        self.fun_lbl1.move(50, 525)
        self.fun_lbl1.resize(200, 200)
        # 글씨 크기 변경
        self.fun_lbl1.setFont(QtGui.QFont("돋음", 10))
        self.fun_lbl1.setStyleSheet("Color : red")

        self.fun_lbl2 = QLabel(" " * 80, self)
        self.fun_lbl2.move(50, 545)
        self.fun_lbl2.resize(200, 200)
        self.fun_lbl2.setFont(QtGui.QFont("돋음", 10))
        self.fun_lbl2.setStyleSheet("Color : red")

        self.fun_lbl3 = QLabel(" " * 80, self)
        self.fun_lbl3.move(50, 565)
        self.fun_lbl3.resize(200, 200)
        self.fun_lbl3.setFont(QtGui.QFont("돋음", 10))
        self.fun_lbl3.setStyleSheet("Color : red")

    def camera_line(self):
        camera_group_box = QGroupBox("카메라 라인")
        btn_camera = QtWidgets.QPushButton("Camera On")
        self.label = QLabel(self)
        self.label.move(50, 50)
        self.label.resize(640, 480)
        btn_camera.clicked.connect(self.camera_online)
        vbox = QVBoxLayout()
        vbox.addWidget(btn_camera)
        vbox.addWidget(self.label)
        camera_group_box.setLayout(vbox)
        camera_group_box.setFixedWidth(900)

        return camera_group_box

    def camera_online(self):
        """
        카메라 종료시 오류

        app.cap.release()
        app.cv2.destroyAllWindows()
        """
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()

    def state_line(self):
        state_group_box = QGroupBox("상태 라인")
        return state_group_box

    def checkbox(self):
        check_group_box = QGroupBox("세부기능 선택")
        grid_box = QGridLayout()
        self.slider1_lcd = QLCDNumber(self)
        self.slider1_lcd.display(1)
        self.slider2_lcd = QLCDNumber(self)
        self.slider2_lcd.display(1)
        self.slider3_lcd = QLCDNumber(self)
        self.slider3_lcd.display(1)

        self.check_box_slider1 = QSlider(Qt.Horizontal, self)
        self.check_box_slider1.setRange(1, 50)
        self.check_box_slider1.setSingleStep(1)
        self.check_box_slider1.valueChanged.connect(self.slider1_lcd.display)

        self.check_box_slider2 = QSlider(Qt.Horizontal, self)
        self.check_box_slider2.setRange(1, 50)
        self.check_box_slider2.setSingleStep(1)
        self.check_box_slider2.valueChanged.connect(self.slider2_lcd.display)

        self.check_box_slider3 = QSlider(Qt.Horizontal, self)
        self.check_box_slider3.setRange(1, 50)
        self.check_box_slider3.setSingleStep(1)
        self.check_box_slider3.valueChanged.connect(self.slider3_lcd.display)

        # 체크박스 생성
        self.check_box1 = QCheckBox('마스크 감지', self)
        self.check_box1.stateChanged.connect(self.function1)

        self.check_box2 = QCheckBox('소음 감지', self)
        self.check_box2.stateChanged.connect(self.function2)

        self.check_box3 = QCheckBox('마스크 미착용 움직임 감지', self)
        self.check_box3.stateChanged.connect(self.function3)

        btn_store_check = QtWidgets.QPushButton("저장 및 실행")
        btn_store_check.clicked.connect(self.startTimer)

        grid_box.addWidget(self.check_box1, 0, 0, 1, 3)
        grid_box.addWidget(self.check_box_slider1, 1, 0)
        grid_box.addWidget(self.slider1_lcd, 1, 3)

        grid_box.addWidget(self.check_box2, 2, 0, 1, 3)
        grid_box.addWidget(self.check_box_slider2, 3, 0)
        grid_box.addWidget(self.slider2_lcd, 3, 3)

        grid_box.addWidget(self.check_box3, 4, 0, 1, 3)
        grid_box.addWidget(self.check_box_slider3, 5, 0)
        grid_box.addWidget(self.slider3_lcd, 5, 3)

        grid_box.addWidget(btn_store_check, 6, 0, 1, 3)
        check_group_box.setLayout(grid_box)

        return check_group_box

    def waiting_time(self):
        waiting_time_group_box = QGroupBox("재사용 대기 시간")
        vbox = QVBoxLayout()
        # lb1의 위치 변경 move(가로 위치, 세로 위치)
        self.function1_waiting_time = QLabel("00:00", self)
        self.function2_waiting_time = QLabel("00:00", self)
        self.function3_waiting_time = QLabel("00:00", self)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(QLabel("마스크 미착용"))
        hbox1.addStretch(1)
        hbox1.addWidget(self.function1_waiting_time)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("소음 감지"))
        hbox2.addStretch(1)
        hbox2.addWidget(self.function2_waiting_time)
        vbox.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(QLabel("마스크 미착용 움직임"))
        hbox3.addStretch(1)
        hbox3.addWidget(self.function3_waiting_time)
        vbox.addLayout(hbox3)

        waiting_time_group_box.setLayout(vbox)
        return waiting_time_group_box

    def startTimer(self):
        print(self.check_box_slider1.value())
        print(self.check_box_slider2.value())
        print(self.check_box_slider3.value())
        print(self.check_box1.isChecked())
        print(self.check_box2.isChecked())
        print(self.check_box3.isChecked())

        self.minute_1 = self.check_box_slider1.value() - 1
        self.minute_2 = self.check_box_slider2.value() - 1
        self.minute_3 = self.check_box_slider3.value() - 1

        self.second = 60

        self.myTimer = QtCore.QTimer(self)
        self.myTimer.timeout.connect(self.timerTimeout)
        self.myTimer.start(1000)

    def timerTimeout(self):
        self.second -= 1

        if self.second == 0:
            self.second = 60
            if self.minute_1 == 0:
                self.function1_waiting_time.setText("00:00")
            if self.minute_2 == 0:
                self.function2_waiting_time.setText("00:00")
            if self.minute_3 == 0:
                self.function3_waiting_time.setText("00:00")
            if self.minute_1 <= -1 and self.minute_2 <= -1 and self.minute_3 <= -1:
                self.myTimer.stop()
            self.minute_1 -= 1
            self.minute_2 -= 1
            self.minute_3 -= 1
        self.update_gui()

    def update_gui(self):
        if self.minute_1 >= 0 and self.check_box1.isChecked():
            self.function1_waiting_time.setText(str(self.minute_1) + ":" + str(self.second))
        if self.minute_2 >= 0 and self.check_box2.isChecked():
            self.function2_waiting_time.setText(str(self.minute_2) + ":" + str(self.second))
        if self.minute_3 >= 0 and self.check_box3.isChecked():
            self.function3_waiting_time.setText(str(self.minute_3) + ":" + str(self.second))

    def function1(self, state):
        if state == Qt.Checked:
            self.fun_lbl1.setText("마스크 감지 활성화")
        else:
            self.fun_lbl1.setText(" " * 30)

    def function2(self, state):
        if state == Qt.Checked:
            self.fun_lbl2.setText("소음 감지 활성화")
        else:
            self.fun_lbl2.setText(" " * 50)

    def function3(self, state):
        if state == Qt.Checked:
            self.fun_lbl3.setText("마스크 미착용 움직임 활성화")
        else:
            self.fun_lbl3.setText(" " * 50)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
