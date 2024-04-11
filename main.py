import sys
import os
import re
import time
import numpy as np
import cv2

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from myDesign_win.home import Ui_MainWindow

QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

class DetThread(QThread):
    send_img = pyqtSignal(np.ndarray)

    def __init__(self):
        super(DetThread, self).__init__()
        self.source = 0

    def run(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            print("Error: 无法打开摄像头")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print('Error: 无法读取帧')
                break
            self.send_img.emit(frame)

    def quit(self) -> None:
        self.cap.release()
        super().quit()


class MainWindow(QMainWindow):
    ui = Ui_MainWindow()
    isMaxi = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.miniButton.clicked.connect(self.showMinimized)
        self.ui.maxiButton.clicked.connect(self.maxOrRestore)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.page1Button.clicked.connect(lambda: self.gotoBlock(0))
        self.ui.page2Button.clicked.connect(lambda: self.gotoBlock(1))
        self.ui.page3Button.clicked.connect(lambda: self.gotoBlock(2))
        self.ui.page4Button.clicked.connect(lambda: self.gotoBlock(3))
        self.ui.page5Button.clicked.connect(lambda: self.gotoBlock(4))

        self.detThread = DetThread()
        self.detThread.send_img.connect(lambda x: self.show_video(x, self.ui.out_video))
        self.detThread.start()

    def myClose(self):
        self.detThread.quit()
        self.close()

    def gotoBlock(self, index: int):
        self.ui.stackedWidget.setCurrentIndex(index)

    def maxOrRestore(self):
        if not self.isMaxi:
            self.showMaximized()
            self.isMaxi = True
        else:
            self.showNormal()
            self.isMaxi = False

    @staticmethod
    def show_video(img_src, label):
        try:
            ih, iw, _ = img_src.shape
            w = label.geometry().width()
            h = label.geometry().height()
            # keep original aspect ratio
            if iw/w > ih/h:
                scal = w / iw
                nw = w
                nh = int(scal * ih)
                img_src_ = cv2.resize(img_src, (nw, nh))

            else:
                scal = h / ih
                nw = int(scal * iw)
                nh = h
                img_src_ = cv2.resize(img_src, (nw, nh))

            frame = cv2.cvtColor(img_src_, cv2.COLOR_BGR2RGB)
            img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[2] * frame.shape[1],
                         QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(img))

        except Exception as e:
            print(repr(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
