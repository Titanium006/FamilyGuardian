import sys
import os
import time

import numpy as np
import cv2

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, QDateTime, QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QEvent
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from myDesign_win.home import Ui_MainWindow
from myDesign_win.videoReplay import Ui_Form
from utils.PageTable import PageTable

from ultralytics import YOLO

QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

Datalist = [[]]
RowIndex = 0
pageCount = 15


class DetThread(QThread):
    send_img = pyqtSignal(np.ndarray)
    send_curTime = pyqtSignal(str)
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
                results = self.model(frame)

                # 在帧上可视化结果
                annotated_frame = results[0].plot()

                # # 保存视频帧
                # cv2.imwrite(os.path.join(self.save_folder, f'{frame_count}.jpg'), annotated_frame)

                # 写入视频
                self.out.write(annotated_frame)

                self.updateTime()
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

    def updateTime(self):
        time = QDateTime.currentDateTime()  # 获取现在的时间
        # timeplay = time.toString('yyyy-MM-dd hh:mm:ss dddd')  # 设置显示时间的格式
        timeplay = time.toString('yyyy-MM-dd hh:mm:ss')  # 设置显示时间的格式
        # print(timeplay)
        self.send_curTime.emit(timeplay)


class VideoReplayWindow(QWidget):
    ui = Ui_Form()
    closing = pyqtSignal()
    videoPath = ''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
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

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        print('进入closeEvent!')
        if self.player.state() == QMediaPlayer.PlayingState or self.player.state() == QMediaPlayer.PausedState:
            self.player.stop()
            # self.player.deleteLater()
        # print('发送关信号前')
        # self.closing.emit()
        # print('发送关闭信号后')
        super().closeEvent(event)

class VideoReplayThread(QThread):
    is_running = True

    def __init__(self, videoPath):
        super(VideoReplayThread, self).__init__()
        # self.videoPath = videoPath
        self.videoWindow = VideoReplayWindow()
        self.videoWindow.videoPath = videoPath

    def run(self):
        self.videoWindow.show()
        # time.sleep(20)
        # self.videoWindow.closing.connect(self.stop)
        # self.videoWindow.close()

        while self.is_running:
            time.sleep(1)
            continue
        if self.videoWindow.isVisible():
            print('关闭子线程窗口')
            self.videoWindow.close()
            print('After 子线程窗口 close')

        print('子线程结束')

        # self.openVideoFile()

    def stop(self):
        self.is_running = False
    
    def quit(self) -> None:
        self.is_running = False
        print('Thread is Quitting!')
        super().quit()


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
        self.ui.closeButton.clicked.connect(self.myClose)
        self.ui.miniButton.clicked.connect(self.showMinimized)
        self.ui.maxiButton.clicked.connect(self.maxOrRestore)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.page1Button.clicked.connect(lambda: self.gotoBlock(0))
        self.ui.page2Button.clicked.connect(lambda: self.gotoBlock(1))
        self.ui.page3Button.clicked.connect(lambda: self.gotoBlock(2))
        self.ui.page4Button.clicked.connect(lambda: self.gotoBlock(3))
        self.ui.page5Button.clicked.connect(lambda: self.gotoBlock(4))

        # PageTable
        header = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        self.pageTable = PageTable(header, 5)
        self.ui.testLayout.addLayout(self.pageTable)
        self.pageTable.pageWidget.send_curPage.connect(lambda x: self.PageChange(x))
        self.ui.btnLoadData.clicked.connect(self.BtnLoadDataClick)

        self.detThread = DetThread()
        self.detThread.send_img.connect(lambda x: self.show_video(x, self.ui.out_video))
        self.detThread.send_curTime.connect(lambda x: self.ui.curTimeLabel.setText(x))
        self.detThread.start()

        self.ui.testBtn.clicked.connect(self.videoReplay)
        self.ui.checkBtn.clicked.connect(self.checkThread)

    def myClose(self):
        self.detThread.quit()
        for thread in self.replayThreads:
            if thread.isRunning():
                thread.stop()
                # thread.wait()
                print('After Wait')
        print('关闭主窗口')
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

    def videoReplay(self):
        path = './v.f100830.mp4'
        replayThread = VideoReplayThread(path)
        self.replayThreads.append(replayThread)
        replayThread.start()

    def checkThread(self):
        for thread in self.replayThreads:
            print(thread.isRunning())

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
