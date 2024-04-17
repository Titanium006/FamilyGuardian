import sys
import os
import time

import numpy as np
import cv2

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, QDateTime, QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QFileDialog, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QEvent, QRect
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QEnterEvent, QColor, QCursor
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from myDesign_win.home import Ui_MainWindow
from myDesign_win.videoReplay import Ui_Form
from utils.PageTable import PageTable
import sqlite3 as sql

from ultralytics import YOLO

QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

Datalist = [[]]
RowIndex = 0
pageCount = 15


class DetThread(QThread):
    send_img = pyqtSignal(np.ndarray)
    # send_curTime = pyqtSignal(str)
    Timer = QTimer()  # 自定义QTimer类

    def __init__(self):
        super(DetThread, self).__init__()
        self.source = 0
        self.model = YOLO('./pt/best.pt')
        self.save_folder = './detect_results/'
        os.makedirs(self.save_folder, exist_ok=True)
        folder_count = 1
        while os.path.exists(os.path.join(self.save_folder, str(folder_count))):
            folder_count += 1
        self.save_folder = os.path.join(self.save_folder, str(folder_count))
        os.makedirs(self.save_folder)

    def run(self):
        self.cap = cv2.VideoCapture(self.source)
        # 视频帧计数器
        frame_count = 0

        # 视频帧宽高
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 视频帧写入对象
        self.out = cv2.VideoWriter(os.path.join(self.save_folder, 'output.mp4'), cv2.VideoWriter_fourcc(*'XVID'), 30,
                                   (frame_width, frame_height))

        # 遍历视频帧
        while self.cap.isOpened():
            # 从视频中读取一帧
            success, frame = self.cap.read()

            if success:
                # 在该帧上运行YOLOv8推理
                results = self.model(frame, verbose=False)

                # 在帧上可视化结果
                annotated_frame = results[0].plot()

                # 图像上写入当前时间
                timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 获取当前时间，格式yyyy-mm-dd HH:MM:ss
                timestr = timestr + " Camera" + str(self.source)
                cv2.putText(annotated_frame, timestr, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                # 写入视频
                self.out.write(annotated_frame)

                # self.updateTime()
                self.send_img.emit(annotated_frame)

                # 计数器自增
                frame_count += 1
            else:
                # 如果视频结束则中断循环
                break
        # pass

    def quit(self) -> None:
        self.cap.release()
        self.out.release()
        super().quit()

    # def updateTime(self):
    #     time = QDateTime.currentDateTime()  # 获取现在的时间
    #     # timeplay = time.toString('yyyy-MM-dd hh:mm:ss dddd')  # 设置显示时间的格式
    #     timeplay = time.toString('yyyy-MM-dd hh:mm:ss')  # 设置显示时间的格式
    #     # print(timeplay)
    #     self.send_curTime.emit(timeplay)


class MainWindow(QMainWindow):
    ui = Ui_MainWindow()
    isMaxi = False

    # 这是PageTable实现的变量
    Datalist = [[]]
    RowIndex = 0
    pageCount = 15

    ##############
    replayThreads = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
        # Ui
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.ui.closeButton.clicked.connect(self.myClose)
        self.ui.closeButton.setToolTip('关闭')
        self.ui.miniButton.clicked.connect(self.showMinimized)
        self.ui.miniButton.setToolTip('最小化')
        self.ui.maxiButton.clicked.connect(self.maxOrRestore)
        self.ui.maxiButton.setToolTip('最大化')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.page1Button.clicked.connect(lambda: self.gotoBlock(0))
        self.ui.page2Button.clicked.connect(lambda: self.gotoBlock(1))
        self.ui.page3Button.clicked.connect(lambda: self.gotoBlock(2))
        self.ui.page4Button.clicked.connect(lambda: self.gotoBlock(3))
        self.ui.page5Button.clicked.connect(lambda: self.gotoBlock(4))
        self.ui.titleGroupBox.mouseDoubleClickEvent = self.onTitleBarDoubleClicked
        self.setMouseTracking(True)
        self.ui.centralwidget.setMouseTracking(True)
        self.ui.titleGroupBox.setMouseTracking(True)
        self.ui.closeButton.setMouseTracking(True)
        self.ui.maxiButton.setMouseTracking(True)
        self.ui.miniButton.setMouseTracking(True)
        self.ui.groupBox.installEventFilter(self)
        self.m_flag = False
        self.direction = None

        # PageTable
        header = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        self.pageTable = PageTable(header, 5)
        self.ui.testLayout.addLayout(self.pageTable)
        self.pageTable.pageWidget.send_curPage.connect(lambda x: self.PageChange(x))
        self.ui.btnLoadData.clicked.connect(self.BtnLoadDataClick)

        self.detThread = DetThread()
        self.detThread.send_img.connect(lambda x: self.show_video(x, self.ui.out_video))
        # self.detThread.send_curTime.connect(lambda x: self.ui.curTimeLabel.setText(x))
        self.detThread.start()

        # VideoReplay
        self.sld_video_pressed = False
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.ui.wgt_video)
        self.ui.btn_open.clicked.connect(self.openVideoFile)
        self.ui.btn_play.clicked.connect(self.playVideo)
        self.ui.btn_stop.clicked.connect(self.pauseVideo)
        self.player.positionChanged.connect(self.changeSlider)
        self.ui.sld_video.setTracking(False)
        self.ui.sld_video.sliderReleased.connect(self.releaseSlider)
        self.ui.sld_video.sliderPressed.connect(self.pressSlider)
        self.ui.sld_video.sliderMoved.connect(self.moveSlider)
        self.ui.sld_video.ClickedValue.connect(self.clickedSlider)
        self.ui.sld_audio.valueChanged.connect(self.volumnChange)

    def myClose(self):
        self.detThread.quit()
        self.close()

    def gotoBlock(self, index: int):
        self.ui.stackedWidget.setCurrentIndex(index)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # print('Enter MouseMoveEvent!')
        self.right_edge = QRect(self.width() - 10, 0, self.width(), self.height())
        self.bottom_edge = QRect(0, self.height() - 10, self.width() - 25, self.height())
        self.right_bottom_edge = QRect(self.width() - 25, self.height() - 10, self.width(), self.height())

        self.windowRange = QRect(0, 0, self.width() - 25, self.height() - 10)

        if not self.isMaximized():
            if self.bottom_edge.contains(event.pos()):
                self.setCursor(Qt.SizeVerCursor)
                self.direction = 'bottom'
            elif self.right_edge.contains(event.pos()):
                self.setCursor(Qt.SizeHorCursor)
                self.direction = 'right'
            elif self.right_bottom_edge.contains(event.pos()):
                self.setCursor(Qt.SizeFDiagCursor)
                self.direction = 'right_bottom'
            elif self.windowRange.contains(event.pos()):
                self.setCursor(Qt.ArrowCursor)
                self.direction = 'None'
                if Qt.LeftButton and self.m_flag:
                    self.move(QCursor.pos() - self.m_Position)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.m_flag = False

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.m_Position = event.pos()
        if event.button() == Qt.LeftButton:
            if self.direction == 'bottom':
                self.windowHandle().startSystemResize(Qt.BottomEdge)
            elif self.direction == 'right':
                self.windowHandle().startSystemResize(Qt.RightEdge)
            elif self.direction == 'right_bottom':
                self.windowHandle().startSystemResize(Qt.RightEdge | Qt.BottomEdge)
            elif 0 < self.m_Position.x() < self.ui.titleGroupBox.pos().x() + self.ui.titleGroupBox.width() and \
                    0 < self.m_Position.y() < self.ui.titleGroupBox.pos().y() + self.ui.titleGroupBox.height():
                self.m_flag = True

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
            self.direction = None
        return super().eventFilter(obj, event)

    def onTitleBarDoubleClicked(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            self.maxOrRestore()

    def maxOrRestore(self):
        if not self.isMaxi:
            self.showMaximized()
            self.isMaxi = True
        else:
            self.showNormal()
            self.isMaxi = False

    def LoadPage(self, pageIndex: int):
        self.Datalist.clear()
        for i in range(self.pageCount):
            Row = []
            self.RowIndex += 1
            Row.append("Data_1_{}_{}".format(self.RowIndex, pageIndex))
            Row.append("Data_2_{}_{}".format(self.RowIndex, pageIndex))
            Row.append("Data_3_{}_{}".format(self.RowIndex, pageIndex))
            Row.append("Data_4_{}_{}".format(self.RowIndex, pageIndex))
            Row.append("Data_5_{}_{}".format(self.RowIndex, pageIndex))
            Row.append("Data_6_{}_{}".format(self.RowIndex, pageIndex))
            Row.append("Data_7_{}_{}".format(self.RowIndex, pageIndex))
            self.Datalist.append(Row)
        self.pageTable.SetData(self.Datalist)

    def BtnLoadDataClick(self):
        self.pageTable.pageWidget.setMaxPage(self.pageCount)
        # print(type(self.pageTable.pageWidget))
        self.pageTable.pageWidget.setCurrentPage(1, True)
        # self.pageTable.pageWidget.setCurrentPage(1, False)
        self.RowIndex = 0
        self.LoadPage(1)

    def PageChange(self, currentPage: int):
        self.LoadPage(currentPage)

    # VideoReplay
    def volumnChange(self, position):
        volume = round(position / self.ui.sld_audio.maximum() * 100)
        print("volume %f" % volume)
        self.player.setVolume(volume)
        self.ui.lab_audio.setText("volume:" + str(volume) + "%")

    def clickedSlider(self, position):
        if self.player.duration() > 0:
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.ui.lab_video.setText("%.2f%%" % position)
        else:
            self.ui.sld_video.setValue(0)

    def moveSlider(self, position):
        self.sld_video_pressed = True
        if self.player.duration() > 0:
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.ui.lab_video.setText("%.2f%%" % position)

    def pressSlider(self):
        self.sld_video_pressed = True
        print("pressed")

    def releaseSlider(self):
        self.sld_video_pressed = False

    def changeSlider(self, position):
        if not self.sld_video_pressed:
            self.videoLength = self.player.duration() + 0.1
            self.ui.sld_video.setValue(round((position / self.videoLength) * 100))
            self.ui.lab_video.setText("%.2f%%" % ((position / self.videoLength) * 100))

    def openVideoFile(self):
        # video_url = QUrl(self.videoPath)
        # self.player.setMedia(QMediaContent(video_url))
        self.player.setMedia(QMediaContent(QFileDialog.getOpenFileUrl()[0]))  # 选取视频文件
        self.player.play()

    def playVideo(self):
        self.player.play()

    def pauseVideo(self):
        self.player.pause()

    # 628×471
    @staticmethod
    def show_video(img_src, label):
        try:
            ih, iw, _ = img_src.shape
            w = label.geometry().width()
            h = label.geometry().height()
            # keep original aspect ratio
            if iw / w > ih / h:
                scal = w / iw
                nw = w
                nh = int(scal * ih)
                img_src_ = cv2.resize(img_src, (nw, nh))
                # print(f'宽: {nw} 高: {nh}')

            else:
                scal = h / ih
                nw = int(scal * iw)
                nh = h
                img_src_ = cv2.resize(img_src, (nw, nh))
                # print(f'宽: {nw} 高: {nh}')

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
