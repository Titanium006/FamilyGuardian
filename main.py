import math
import sys
import os
import re
import time

import numpy as np
import cv2
import sqlite3 as sql

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, QDateTime, QUrl, QDate
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QFileDialog, QGraphicsDropShadowEffect, \
    QMessageBox, QLineEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QEvent, QRect
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QEnterEvent, QColor, QCursor
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from myDesign_win.home import Ui_MainWindow
from myDesign_win.videoReplay import Ui_Form
from myDesign_win.newUser import Ui_Dialog as Ui_newUserDialog
from myDesign_win.loginSurface import Ui_Dialog
from utils.PageTable import PageTable
from utils.PageButton import PageButton, UserDelButton
from utils.encryption import func_encrypt_config, func_decrypt_config
from utils.lineEditValidator import LineEditValidator

from ultralytics import YOLO
from datetime import datetime

# 设置这个可以确保屏幕分辨率不影响界面显示
QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
key = b'mysecretpassword'  # 密钥（需要确保安全）


class DetThread(QThread):
    send_img = pyqtSignal(np.ndarray)
    send_curInsertID = pyqtSignal(int)

    def __init__(self, videoSavePath, threshold=1000):
        super(DetThread, self).__init__()
        self.curInsertID = 211
        self.source = 0
        self.threshold = threshold  # 设置数据库存储报警信息条数的阈值, 超过这个阈值就开始删除老数据
        self.model = YOLO('./pt/best.pt')  # 这个先不改, 看看后面模型放哪先
        self.save_folder = videoSavePath + '/detect_results/'
        os.makedirs(self.save_folder, exist_ok=True)
        self._initSaveTime()

    def _initSaveTime(self):
        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y%m%d")  # 将 current_time 转换为字符串形式，格式为年月日时分秒
        self.save_folder = os.path.join(self.save_folder, current_time_str)
        print('Current save_folder is {}!'.format(self.save_folder))
        os.makedirs(self.save_folder, exist_ok=True)
        # 初始化各类别的计数器和开始时间
        self.smoke_count = 0
        self.fire_count = 0
        self.person_count = 0
        self.smoke_start_time = None
        self.fire_start_time = None
        self.person_start_time = None
        self.smoke_locked = False
        self.fire_locked = False
        self.person_locked = False
        # 添加结束时间变量
        self.smoke_end_count = 0
        self.fire_end_count = 0
        self.person_end_count = 0
        self.smoke_end_time = None
        self.fire_end_time = None
        self.person_end_time = None

    def run(self):
        self.cap = cv2.VideoCapture(self.source)
        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")  # 将 current_time 转换为字符串形式，格式为年月日时分秒
        self.video_filename = f"{current_time_str}.mp4"  # 使用 current_time_str 作为视频文件名的一部分
        # 视频帧计数器
        frame_count = 0

        # 视频帧宽高
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 视频帧写入对象
        ori_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        if ori_fps == 0:
            ori_fps = 25
        self.out = cv2.VideoWriter(os.path.join(self.save_folder, self.video_filename), cv2.VideoWriter_fourcc(*'mp4v'),
                                   5,
                                   (frame_width, frame_height))

        # 遍历视频帧
        while self.cap.isOpened():
            # 从视频中读取一帧
            success, frame = self.cap.read()
            current_frame_time = datetime.now()

            if success:
                # 在该帧上运行YOLOv8推理
                results = self.model(frame, verbose=False)
                for r in results:
                    # 检查张量是否为空
                    if r.boxes.cls.numel() == 0:
                        # 在这里添加适当的处理代码，例如跳过当前循环迭代
                        continue
                    cls = int(r.boxes.cls[0])
                    # 检测到烟雾
                    if cls == 0:
                        # 如果是第一次检测到烟雾，记录开始时间
                        if self.smoke_start_time is None:
                            self.smoke_start_time = current_frame_time

                        if not self.smoke_locked:
                            self.check_reset_smoke_start_time(current_frame_time)
                            self.smoke_count += 1  # 每次检测到人，计数器加1

                    # 检测到火焰
                    elif cls == 1:
                        # 如果是第一次检测到火焰，记录开始时间
                        if self.fire_start_time is None:
                            self.fire_start_time = current_frame_time

                        if not self.fire_locked:
                            self.check_reset_fire_start_time(current_frame_time)
                            self.fire_count += 1  # 每次检测到人，计数器加1

                    # 检测到人
                    elif cls == 2:
                        # 如果是第一次检测到人，记录开始时间
                        if self.person_start_time is None:
                            self.person_start_time = current_frame_time

                        if not self.person_locked:
                            self.check_reset_person_start_time(current_frame_time)
                            self.person_count += 1  # 每次检测到人，计数器加1
                        # print(self.person_count)

                    # 添加结束时间记录逻辑
                    if self.smoke_start_time is not None and self.smoke_locked:
                        if self.smoke_end_time is None:
                            self.smoke_end_time = current_frame_time
                        if cls == 0:
                            self.smoke_end_count += 1

                    if self.fire_start_time is not None and self.fire_locked:
                        if self.fire_end_time is None:
                            self.fire_end_time = current_frame_time
                        if cls == 1:
                            self.fire_end_count += 1

                    if self.person_start_time is not None and self.person_locked:
                        if self.person_end_time is None:
                            self.person_end_time = current_frame_time
                        if cls == 2:
                            self.person_end_count += 1
                            # print(self.person_end_count)

                    self.check_reset_end_time(current_frame_time)

                # 在帧上可视化结果
                annotated_frame = results[0].plot()

                # 图像上写入当前时间
                timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 获取当前时间，格式yyyy-mm-dd HH:MM:ss
                timestr = timestr + " Camera" + str(self.source)
                cv2.putText(annotated_frame, timestr, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                # # 保存视频帧
                # cv2.imwrite(os.path.join(self.save_folder, f'{frame_count}.jpg'), annotated_frame)

                # 写入视频
                self.out.write(annotated_frame)

                self.send_img.emit(annotated_frame)

                # 计数器自增
                frame_count += 1
            else:
                # 如果视频结束则中断循环
                break
        # pass

    def check_reset_smoke_start_time(self, current_time):
        # 计算当前时间和最后一次记录时间的差值
        time_diff = (current_time - self.smoke_start_time).total_seconds() * 1000

        if time_diff >= 1000:  # 超过一秒
            if self.smoke_count < 5:
                # 如果计数小于5，重置计数器和开始时间
                self.smoke_count = 0
                self.smoke_start_time = current_time
            else:
                # 如果计数大于等于5，锁定计数器和开始时间，停止计数
                self.smoke_locked = True  # 假设有一个 locked 属性用于锁定计数器

    def check_reset_fire_start_time(self, current_time):
        # 计算当前时间和最后一次记录时间的差值
        time_diff = (current_time - self.fire_start_time).total_seconds() * 1000

        if time_diff >= 1000:  # 超过一秒
            if self.fire_count < 5:
                # 如果计数小于5，重置计数器和开始时间
                self.fire_count = 0
                self.fire_start_time = current_time
            else:
                # 如果计数大于等于5，锁定计数器和开始时间，停止计数
                self.fire_locked = True  # 假设有一个 locked 属性用于锁定计数器

    def check_reset_person_start_time(self, current_time):
        # 计算当前时间和最后一次记录时间的差值
        time_diff = (current_time - self.person_start_time).total_seconds() * 1000

        if time_diff >= 1000:  # 超过一秒
            if self.person_count < 5:
                # 如果计数小于5，重置计数器和开始时间
                self.person_count = 0
                self.person_start_time = current_time
            else:
                # 如果计数大于等于5，锁定计数器和开始时间，停止计数
                self.person_locked = True  # 假设有一个 locked 属性用于锁定计数器

    def check_reset_end_time(self, current_time):
        # 添加结束时间处理逻辑
        if self.smoke_end_time is not None:
            if (current_time - self.smoke_end_time).total_seconds() * 1000 >= 1000:
                if self.smoke_end_count < 5:
                    saved_successfully = self.save_if_threshold_exceeded(self.smoke_count, self.smoke_end_count,
                                                                         self.smoke_start_time,
                                                                         self.smoke_end_time, '0')
                    # 检查文件是否保存成功
                    if saved_successfully:
                        self.smoke_count = 0
                        self.smoke_end_count = 0
                        self.smoke_start_time = None
                        self.smoke_end_time = None
                        self.smoke_locked = False
                else:
                    self.smoke_end_count = 0
                    self.smoke_end_time = None

        if self.fire_end_time is not None:
            if (current_time - self.fire_end_time).total_seconds() * 1000 >= 1000:
                if self.fire_end_count < 5:
                    saved_successfully = self.save_if_threshold_exceeded(self.fire_count, self.fire_end_count,
                                                                         self.fire_start_time,
                                                                         self.fire_end_time, '1')
                    # 检查文件是否保存成功
                    if saved_successfully:
                        self.fire_count = 0
                        self.fire_end_count = 0
                        self.fire_start_time = None
                        self.fire_end_time = None
                        self.fire_locked = False
                else:
                    self.fire_end_count = 0
                    self.fire_end_time = None

        if self.person_end_time is not None:
            if (current_time - self.person_end_time).total_seconds() * 1000 >= 1000:
                if self.person_end_count < 5:
                    saved_successfully = self.save_if_threshold_exceeded(self.person_count, self.person_end_count,
                                                                         self.person_start_time,
                                                                         self.person_end_time, '2')
                    # 检查文件是否保存成功
                    if saved_successfully:
                        self.person_count = 0
                        self.person_end_count = 0
                        self.person_start_time = None
                        self.person_end_time = None
                        self.person_locked = False
                else:
                    self.person_end_count = 0
                    self.person_end_time = None

    def save_if_threshold_exceeded(self, start_count, end_count, start_time, end_time, cls):
        # 如果计数器超过阈值
        # print('Enter save_if_threshold_exceeded!')
        if start_count > 5 > end_count:
            start_time_str = start_time.strftime('%Y-%m-%d_%H-%M-%S')
            end_time_str = end_time.strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'{cls}_' + start_time_str + '__' + end_time_str + '.txt'
            # 构建文件路径
            filepath = os.path.join(self.save_folder, filename)
            # 保存开始时间和类别到文本文件
            self.saveTimestamp(start_time, end_time, filepath, cls)
            return True
        else:
            return False

    def saveTimestamp(self, start_time, end_time, filepath, cls):
        # 格式化开始时间和结束时间为字符串
        start_time_str = start_time.strftime('%Y-%m-%d_%H-%M-%S')
        end_time_str = end_time.strftime('%Y-%m-%d_%H-%M-%S')
        # print('Ready to write {}!'.format(filepath))
        # 将时间戳写入文本文件
        with open(filepath, 'w') as file:
            file.write('{} {} {}'.format(cls, start_time_str, end_time_str))

    def quit(self) -> None:
        self.cap.release()
        self.out.release()
        time.sleep(2)
        filepath = os.path.join(self.save_folder, self.video_filename)
        if os.path.isfile(filepath):
            basename, extension = os.path.splitext(self.video_filename)
            endTimeStr = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            new_name = f"{basename}_{endTimeStr}_{self.source}{extension}"
            new_file_path = os.path.join(self.save_folder, new_name)
            os.rename(filepath, new_file_path)
        super().quit()


class MainWindow(QMainWindow):
    ui = Ui_MainWindow()
    isMaxi = False

    # DetThread
    curInsertID = 211  # 这是当前(未)插入的最新id    (满减实现逻辑等我后面再写)
    threshold = 1000  # 数据库报警信息插入条数阈值

    # 这是PageTable实现的变量
    Datalist = [()]
    # RowIndex = 0
    # pageCount = 15

    alarmRowCount = 15
    totalLinesCnt = 0  # 当前获取到的报警条数

    ##############
    searchRowCnt = 10
    videoFileSavePath = 'D:/大三下/软工课设/HomeSurface'
    videoFileSaveFolder = 'detect_results'
    SearchDatalist = [[]]

    UserDatalist = [[]]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
        self._initUi()
        self._initPageTable()
        self._initDetThread()
        self._initVideoReplay()
        self._initDatabase()
        self._initVideoSearch()
        self._initUserPage()

    def videoReplay(self, infoGroup):
        # seperator = ' '
        # infoGroup[-1] = str(infoGroup[-1])
        # infoGroup[-2] = str(infoGroup[-2])
        # # print(infoGroup)
        # result = seperator.join(infoGroup)
        # # print(result)
        # QMessageBox.information(self, '', result)  # 注意是.information 不是构造函数
        if len(infoGroup[-2]) != 0:
            absolute_path = os.path.join(self.videoFileSavePath, self.videoFileSaveFolder, self.folderName, infoGroup[-2])
            self.rtPageIndex = 3
            if not self.openVideoFile(absolute_path):
                self.rtPageIndex = 0
                QMessageBox.information(self, '', '回放文件已被清理!')
        else:
            pass

    def myClose(self):
        self.detThread.quit()
        self.conn.commit()  # 这里提交用户账号信息的修改, 防止出现同时写的报错和不一致情况
        self.conn.close()
        self.close()

    def gotoBlock(self, index: int):
        # 设置跳转之后的初始刷新, 如果没有就会导致页面显示混乱
        if index == 1:
            self.BtnLoadDataClick()
        elif index == 3:
            self.BtnQureyClick()
        else:
            self.updateUserPage()
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
        # 实现读取数据操作
        c = self.conn.cursor()
        # 检查当前的插入id号, 分(满)和(不满)两种情况处理
        if self.totalLinesCnt < self.threshold:  # 小于阈值, 正常加载数据
            # 这里应该是设置从pageIndex*self.alarmRowCount的位置开始读取self.alarmRowCount个    或许还是设计一个当前读取到的坐标(指针)比较好
            c.execute("SELECT startTime, endTime, alarmType, camNo FROM alarmRecord ORDER BY id DESC LIMIT ? OFFSET ?",
                      (self.alarmRowCount,
                       self.alarmRowCount * (pageIndex - 1)))
            rows = c.fetchall()
            j = 0
            for i, row in enumerate(rows, self.alarmRowCount * (pageIndex - 1) + 1):
                button = self.pageButtons[j]
                button.startTime = row[0]
                button.endTime = row[1]
                button.camNo = row[-1]
                self.Datalist.append((i,) + row + (button,))  # 在每行的前面添加序号
                j += 1

        self.pageTable.SetData(self.Datalist)

    def BtnLoadDataClick(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM alarmRecord")
        self.totalLinesCnt = c.fetchone()[0]
        self.pageTable.pageWidget.setMaxPage(math.ceil(self.totalLinesCnt / self.alarmRowCount))
        # print(type(self.pageTable.pageWidget))
        self.pageTable.pageWidget.setCurrentPage(1, True)
        # self.pageTable.pageWidget.setCurrentPage(1, False)
        # self.RowIndex = 0
        self.LoadPage(1)

    def PageChange(self, currentPage: int):
        self.LoadPage(currentPage)

    # VideoReplay
    def volumnChange(self, position):
        volume = round(position / self.ui.sld_audio.maximum() * 100)
        # print("volume %f" % volume)
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

    def openVideoFile(self, absolutePath: str) -> bool:
        if os.path.isfile(absolutePath):
            self.gotoBlock(2)
            mediaContent = QMediaContent(QUrl.fromLocalFile(absolutePath))
            self.player.setMedia(mediaContent)  # 选取视频文件
            self.player.play()
            return True
        else:
            return False

    def playVideo(self):
        self.player.play()

    def pauseVideo(self):
        self.player.pause()

    def _initUi(self):
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

    def _initDatabase(self):
        self.dataBaseName = 'myDB.db'
        self.conn = sql.connect(self.dataBaseName, isolation_level=None, uri=True)  # 启用WAL模式
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS alarmRecord 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                    startTime TEXT NOT NULL, 
                    endTime TEXT NOT NULL, 
                    alarmType INTEGER NOT NULL, 
                    camNo INTEGER NOT NULL)
        ''')
        self.conn.commit()

    def _initPageTable(self):
        # PageTable
        header = ["序号", "开始时间", "结束时间", "报警类型", "摄像头编号", "操作"]
        self.pageTable = PageTable(header, self.alarmRowCount)
        self.ui.testLayout.addLayout(self.pageTable)
        self.pageTable.pageWidget.send_curPage.connect(lambda x: self.PageChange(x))
        self.ui.btnLoadData.clicked.connect(self.BtnLoadDataClick)
        self.pageButtons = []
        for i in range(self.alarmRowCount):
            button = PageButton()
            button.btnNo = i + 1
            button.setText('回 放')
            button.send_myNo.connect(lambda x: self.videoReplay(x))
            self.pageButtons.append(button)

    def _initVideoSearch(self):
        self.ui.dateEdit.setDate(QDate.currentDate())
        header = ["序号", "录像名称", "开始时间", "结束时间", "摄像头编号", "文件大小", "操作"]
        self.searchTable = PageTable(header, self.searchRowCnt)
        self.ui.searchLayout.addLayout(self.searchTable)
        self.searchTable.pageWidget.send_curPage.connect(lambda x: self.searchPageChange(x))
        self.ui.queryButton.clicked.connect(self.BtnQureyClick)
        self.searchPageButtons = []
        for i in range(self.searchRowCnt):
            button = PageButton()
            button.btnNo = i + 1
            button.setText('回 放')
            button.send_myNo.connect(lambda x: self.videoReplay(x))
            self.searchPageButtons.append(button)

    def searchPageChange(self, currentPage: int):
        self.LoadSearchPage(currentPage)

    def LoadSearchPage(self, currentPage: int):
        self.SearchDatalist.clear()
        leftBorfer = (currentPage - 1) * self.searchRowCnt
        rightBorder = currentPage * self.searchRowCnt
        if currentPage * self.searchRowCnt > len(self.mp4Files):
            rightBorder = len(self.mp4Files)
        for i in range(leftBorfer, rightBorder):
            button = self.searchPageButtons[i % self.searchRowCnt]
            button.startTime = self.timestampGroup[i][0]
            button.endTime = self.timestampGroup[i][-1]
            button.camNo = self.cameraNums[i]
            button.btnNo = (i + 1) % self.searchRowCnt
            if button.btnNo == 0:
                button.btnNo = self.searchRowCnt
            button.fileName = self.mp4Files[i]
            # print('button.fileName is ' + button.fileName)
            tempList = [str(i + 1)] + [self.mp4Files[i]] + self.timestampGroup[i] + [str(self.cameraNums[i])] + \
                       [str(self.fileSizes[i])] + [self.searchPageButtons[i % self.searchRowCnt]]
            self.SearchDatalist.append(tempList)
        # print(self.SearchDatalist)
        self.searchTable.SetData(self.SearchDatalist)

    def BtnQureyClick(self):
        # 获取QDateEdit里面的内容, 然后根据它去查找视频回放 (定义好文件夹和视频的保存路径以及文件名称
        selected_date = self.ui.dateEdit.date()
        # print("Selected Date: ", selected_date.toString("yyyy-MM-dd"))
        self.folderName = selected_date.toString("yyyyMMdd")
        # print(folderName)
        if os.path.exists(os.path.join(self.videoFileSavePath + '/detect_results', self.folderName)):
            self.mp4Files, self.fileSizes = self.get_mp4_files(
                os.path.join(self.videoFileSavePath + '/detect_results', self.folderName))
            self.timestampGroup = []
            self.cameraNums = []
            for mp4file in self.mp4Files:
                timestamps, cameraNumber = self.extract_timestamps_cameraNumber(mp4file)
                tmpstamp = []
                for timestamp in timestamps:
                    tmpstamp.append(self.transform_timestamp(timestamp))
                self.timestampGroup.append(tmpstamp)
                self.cameraNums.append(cameraNumber)
            self.searchTable.pageWidget.setMaxPage(math.ceil(len(self.mp4Files) / self.searchRowCnt))
            self.searchTable.pageWidget.setCurrentPage(1, True)
            self.LoadSearchPage(1)
        else:
            QMessageBox.information(self, '', '暂无可查看回放！')
            return

    def get_mp4_files(self, directory):
        mp4_files = []
        file_sizes = []
        # 获取目录中所有文件和子目录
        files = os.listdir(directory)
        pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_\d+\.mp4$'
        # 遍历文件列表
        for file in files:
            # 构建文件的完整路径
            file_path = os.path.join(directory, file)
            # 判断是否为文件以及是否为MP4文件
            if os.path.isfile(file_path) and file.lower().endswith('.mp4') and re.match(pattern, file):
                # print(os.path.basename(file_path))
                # 提取文件名部分，并添加到列表中
                mp4_files.append(os.path.basename(file_path))
                fileSizeBytes = os.path.getsize(file_path)
                fileSizeMB = round(fileSizeBytes / (1024 * 1024), 2)
                file_sizes.append(fileSizeMB)
        return mp4_files, file_sizes

    def extract_timestamps_cameraNumber(self, filename):
        # 定义日期时间格式的正则表达式模式
        pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
        # 在文件名中搜索匹配的日期时间字符串
        timestamps = re.findall(pattern, filename)
        parts = filename.split('_')
        camereNumber = parts[-1].split('.')[0]
        return timestamps, camereNumber

    def transform_timestamp(self, timestamp):
        stamplist = timestamp.split('_')
        # 将时间戳中的 '_' 替换为 ' '，将 '-' 替换为 ':'，得到新的格式
        transformed_timestamp = stamplist[-1].replace('-', ':')
        timestamp_new = stamplist[0] + ' ' + transformed_timestamp
        return timestamp_new

    def _initDetThread(self):
        # detThread
        self.detThread = DetThread(self.videoFileSavePath, self.threshold)
        self.detThread.send_img.connect(lambda x: self.show_video(x, self.ui.out_video))
        self.detThread.send_curInsertID.connect(lambda x: self.updateCurInsertID(x))
        self.detThread.start()

    def _initVideoReplay(self):
        # VideoReplay
        self.sld_video_pressed = False
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.ui.wgt_video)
        self.ui.btn_play.clicked.connect(self.playVideo)
        self.ui.btn_stop.clicked.connect(self.pauseVideo)
        self.player.positionChanged.connect(self.changeSlider)
        self.ui.sld_video.setTracking(False)
        self.ui.sld_video.sliderReleased.connect(self.releaseSlider)
        self.ui.sld_video.sliderPressed.connect(self.pressSlider)
        self.ui.sld_video.sliderMoved.connect(self.moveSlider)
        self.ui.sld_video.ClickedValue.connect(self.clickedSlider)
        self.ui.sld_audio.valueChanged.connect(self.volumnChange)
        self.rtPageIndex = 0    # 返回的页面下标
        self.ui.returnBtn.clicked.connect(self.rtBlock)

    def rtBlock(self):
        self.player.stop()
        self.gotoBlock(self.rtPageIndex)

    def updateCurInsertID(self, id: int):
        self.curInsertID = id

    def _initUserPage(self):
        self.ui.userAddBtn.clicked.connect(self.addUser)
        self.userpageRowCnt = 8
        header = ["序号", "用户名", "密码", "操作"]
        self.userTable = PageTable(header, self.userpageRowCnt)
        self.ui.userLayout.addLayout(self.userTable)
        self.userTable.pageWidget.send_curPage.connect(lambda x: self.userPageChange(x))
        self.userPageButtons = []
        for i in range(self.userpageRowCnt):
            button = UserDelButton()
            button.btnNo = i + 1
            button.setText('删 除')
            button.send_myNo.connect(lambda x: self.deleteUser(x))
            self.userPageButtons.append(button)

    def userPageChange(self, currenPage: int):
        self.LoadUserPage(currenPage)

    def LoadUserPage(self, currentPage: int):
        self.UserDatalist.clear()
        c = self.conn.cursor()
        c.execute("SELECT userID, userCode FROM userInfo LIMIT ? OFFSET ?",
                  (self.userpageRowCnt, self.userpageRowCnt * (currentPage - 1)))
        rows = c.fetchall()
        j = 0
        for i, row in enumerate(rows, self.userpageRowCnt * (currentPage - 1) + 1):
            button = self.userPageButtons[j]
            tmpList = [i]
            button.userID = row[0]
            tmpList.append(button.userID)
            code = func_decrypt_config(key, row[1])
            hideCode = '*' * len(code)
            tmpList.append(hideCode)
            tmpList.append(button)
            self.UserDatalist.append(tmpList)
            j += 1
        # print(self.UserDatalist)
        self.userTable.SetData(self.UserDatalist)

    def updateUserPage(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM userInfo")
        self.totalUserCnt = c.fetchone()[0]
        self.userTable.pageWidget.setMaxPage(math.ceil(self.totalUserCnt / self.userpageRowCnt))
        self.userTable.pageWidget.setCurrentPage(1, True)
        self.LoadUserPage(1)

    def deleteUser(self, infoGroup):
        if self.totalUserCnt == 1:
            QMessageBox.information(self, '', '无法删除唯一的用户!')
        else:
            msgBox = QMessageBox()
            msgBox.setText('确定要删除该用户吗?')
            msgBox.addButton(QMessageBox.Yes)
            msgBox.addButton(QMessageBox.No)
            response = msgBox.exec_()
            if response == QMessageBox.Yes:
                # print('userIDtodel:' + infoGroup[0])
                userID = infoGroup[0]
                c = self.conn.cursor()
                # print('encryptedID: ' + userID)
                c.execute('DELETE FROM userInfo WHERE userID = ?', (userID,))
                self.conn.commit()
                self.updateUserPage()

    def addUser(self):
        self.regisDialog = registerDialog(firstIn=False)
        self.regisDialog.setFixedSize(378, 440)
        self.regisDialog.exec_()
        self.updateUserPage()

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


class registerDialog(QDialog):
    abnormalExit = False  # 用于给程序知道是非正常退出，可以不用展示后面的界面
    ui = Ui_newUserDialog()
    userNameValidator = LineEditValidator(
        fullPatterns=['', r'^[a-zA-Z0-9]{6,12}$'],
        partialPatterns=['', r'^[a-zA-Z0-9]{1,12}$'],
        fixupString=''
    )
    userPasswordValidator = LineEditValidator(
        fullPatterns=['', r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z0-9]{8,16}$'],
        partialPatterns=['', r'^[a-zA-Z0-9]{1,16}$'],
        fixupString=''
    )

    def __init__(self, firstIn=True, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.regisMiniButton.clicked.connect(self.showMinimized)
        self.ui.regisCloseButton.clicked.connect(self.reject)  # 这里要设置让后面的东西别出来了
        self.ui.userNameEdit.setValidator(self.userNameValidator)
        self.ui.userNameEdit.installEventFilter(self.userNameValidator)
        self.ui.userNameEdit.setPlaceholderText('6-12个英文/数字组合')
        self.ui.passwordEdit.setEchoMode(QLineEdit.Password)
        self.ui.passwordEdit.setValidator(self.userPasswordValidator)
        self.ui.passwordEdit.installEventFilter(self.userPasswordValidator)
        self.ui.passwordEdit.setPlaceholderText('8-16个英文/数字组合(至少一个英文大小写加数字)')
        self.ui.passwordConfirmEdit.setValidator(self.userPasswordValidator)
        self.ui.passwordConfirmEdit.installEventFilter(self.userPasswordValidator)
        self.ui.passwordConfirmEdit.setEchoMode(QLineEdit.Password)
        self.ui.passwordConfirmEdit.setPlaceholderText('与第一次的输入保持一致')
        self.ui.registerButton.clicked.connect(self.register)
        self.databaseName = 'myDB.db'
        self.conn = sql.connect(self.databaseName, isolation_level=None, uri=True)  # 启用WAL模式
        self.firstIn = firstIn
        if firstIn:
            QMessageBox.information(self, '', '首次登录，请先创建用户!')

    def register(self):
        userInput_Name = self.ui.userNameEdit.text()
        userInput_Password = self.ui.passwordEdit.text()
        userInput_PasswordConfirm = self.ui.passwordConfirmEdit.text()
        if len(userInput_Name) == 0 or len(userInput_Password) == 0 or len(userInput_PasswordConfirm) == 0:
            QMessageBox.information(self, '', '用户名/密码不能为空!')
            self.ui.userNameEdit.setFocus()
            return
        if userInput_Password != userInput_PasswordConfirm:
            QMessageBox.information(self, '', '两次输入的密码不一致!')
            self.ui.passwordEdit.clear()
            self.ui.passwordConfirmEdit.clear()
            self.ui.passwordEdit.setFocus()
            return
        c = self.conn.cursor()
        # userID = func_encrypt_config(key, userInput_Name)
        userCode = func_encrypt_config(key, userInput_Password)
        c.execute('INSERT INTO userInfo (userID, userCode) VALUES (?, ?)', (userInput_Name, userCode))
        if self.firstIn:
            # 注册成功
            msgBox = QMessageBox()
            msgBox.setText('注册成功!\n即将转到登陆界面...')
            timer = QTimer()
            timer.timeout.connect(msgBox.close)
            timer.start(3000)
            msgBox.exec_()
        self.conn.close()
        self.accept()


class loginDialog(QDialog):
    ui = Ui_Dialog()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.loginButton.clicked.connect(self.check)
        self.ui.loginMiniButton.clicked.connect(self.showMinimized)
        self.ui.loginCloseButton.clicked.connect(self.reject)
        # self.ui.loginCloseButton.clicked.connect(self.close)
        self.ui.passwordEdit.setEchoMode(QLineEdit.Password)
        self.tryLoginTimes = 4
        self.databaseName = 'myDB.db'
        self.conn = sql.connect(self.databaseName, isolation_level=None, uri=True)

    def check(self):
        # print('Enter Check!')
        c = self.conn.cursor()
        c.execute('SELECT * FROM userInfo')
        rows = c.fetchall()
        userInfo = ''
        for row in rows:
            userID, userCode = row
            userInfo = userInfo + userID + '\n' + func_decrypt_config(key, userCode) + '\n'
        # print('Get userInfo:' + userInfo)
        userInput_Name = self.ui.userNameEdit.text()
        userInput_Password = self.ui.passwordEdit.text()
        if self.check_credentials(userInfo, userInput_Name, userInput_Password) == 1:
            print('登录成功!')
            # QMessageBox.information(self, 'Congratulation!', '登陆成功!')
            msgBox = QMessageBox()
            msgBox.setText('登陆成功!')
            timer = QTimer()
            timer.timeout.connect(msgBox.close)
            timer.start(2000)
            msgBox.exec_()
            print('Ready to Accept!')
            self.conn.close()
            self.accept()
        elif self.check_credentials(userInfo, userInput_Name, userInput_Password) == 2:
            print('密码错误!')
            self.ui.passwordEdit.clear()
            self.tryLoginTimes -= 1
            QMessageBox.information(self, '', '密码错误!你还有{}次机会!'.format(self.tryLoginTimes))
            if self.tryLoginTimes == 0:
                self.conn.close()
                self.reject()
        elif self.check_credentials(userInfo, userInput_Name, userInput_Password) == 3:
            print('账号错误!')
            self.ui.userNameEdit.clear()
            self.ui.passwordEdit.clear()
            self.ui.userNameEdit.setFocus()
            self.tryLoginTimes -= 1
            QMessageBox.information(self, '', '账号错误!你还有{}次机会!'.format(self.tryLoginTimes))
            if self.tryLoginTimes == 0:
                self.conn.close()
                self.reject()

    def check_credentials(self, userinfo, userinput_name, userinput_password):
        lines = userinfo.splitlines()
        userNum = [x for x in range(0, len(lines) - 1) if x % 2 == 0]
        # print('userNum:')
        # print(userNum)
        if len(lines) % 2 != 0:
            raise SystemExit('UserFileError!')
        correctCnt = 0
        codeWrongCnt = 0
        idWrongCnt = 0
        for i in userNum:
            if lines[i] == userinput_name and lines[i + 1] == userinput_password:  # 匹配成功
                correctCnt += 1
            elif lines[i] == userinput_name and lines[i + 1] != userinput_password:  # 密码错误
                codeWrongCnt += 1
            else:  # 账号错误
                idWrongCnt += 1
        if correctCnt != 0:
            return 1
        elif codeWrongCnt != 0:
            return 2
        elif idWrongCnt != 0:
            return 3
        return 0


class Controller:

    def __init__(self):
        self.databaseName = 'myDB.db'
        self.conn = sql.connect(self.databaseName, isolation_level=None, uri=True)
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS userInfo 
                    (userID TEXT PRIMARY KEY NOT NULL,
                    userCode TEXT NOT NULL)
        ''')
        self.conn.commit()

    def show_register(self):
        self.regisDialog = registerDialog()
        self.regisDialog.setFixedSize(378, 440)
        return self.regisDialog.exec_()

    def show_login(self):
        self.logDialog = loginDialog()
        self.logDialog.setFixedSize(378, 440)
        return self.logDialog.exec_()

    def openLoginSurface(self):
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*) FROM userInfo')
        result = c.fetchone()[0]
        self.conn.close()
        # 如果没有用户账户信息，打开注册界面
        if result == 0:
            if self.show_register() == QDialog.Rejected:
                return False
        if self.show_login() == QDialog.Accepted:
            print('Ready to return True!')
            return True
        else:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = Controller()
    if controller.openLoginSurface():
        # print('Enter MainWindow()!')
        Mymainwindow = MainWindow()
        Mymainwindow.show()
    else:
        sys.exit(0)
    sys.exit(app.exec_())
