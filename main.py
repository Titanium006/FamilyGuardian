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
    QMessageBox, QLineEdit, QSizePolicy, QMenu, QAction
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QEvent, QRect, QSize, QPoint
from PyQt5.QtGui import QImage, QPixmap, QMouseEvent, QEnterEvent, QColor, QCursor, QIcon, QGuiApplication
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
from utils.CustomMessageBox import MessageBox
from utils.capnums import Camera
import apprcc_rc

from ultralytics import YOLO
from datetime import datetime, timedelta
import multiprocessing

# 设置这个可以确保屏幕分辨率不影响界面显示
# QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QGuiApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
key = b'mysecretpassword'  # 密钥（需要确保安全）


class DetThread(QThread):
    """
    检测线程类, 用于执行物体检测任务
    Attributes:
        send_img (pyqtSignal): 发送图像信号
        send_infoInsert (pyqtSignal): 发送信息插入信号
        send_showWin (pyqtSignal): 发送显示信息窗口信号
        source: 视频源，默认为摄像头。
        threshold (int): 数据库存储报警信息条数的阈值，超过这个阈值就开始删除老数据。
        model: YOLO模型对象。
        dataBaseName (str): 数据库文件名。
        save_folder (str): 存储检测结果的文件夹路径。
        frameCnt (int): 帧计数器。
        frame_width (int): 视频帧宽度。
        frame_height (int): 视频帧高度。
        checkingStranger (bool): 是否检测陌生人，默认为True。
        detThreshold (int): 检测阈值。
        smoke_count (int): 烟雾检测计数器。
        fire_count (int): 火焰检测计数器。
        person_count (int): 人物检测计数器。
        smoke_start_time (datetime): 烟雾检测开始时间
        fire_start_time (datetime): 火焰检测开始时间。
        person_start_time (datetime): 人物检测开始时间。
        smoke_locked (bool): 是否锁定烟雾检测。
        fire_locked (bool): 是否锁定火焰检测。
        person_locked (bool): 是否锁定人物检测。
        smoke_end_count (int): 烟雾检测结束计数器。
        fire_end_count (int): 火焰检测结束计数器。
        person_end_count (int): 人物检测结束计数器。
        smoke_end_time (datetime): 烟雾检测结束时间。
        fire_end_time (datetime): 火焰检测结束时间。
        person_end_time (datetime): 人物检测结束时间。
        delta (int): 视频打开时间偏移量。
        conn: 数据库连接对象。
        curInsertID (int): 当前插入的报警记录ID。
    """
    send_img = pyqtSignal(np.ndarray)
    send_infoInsert = pyqtSignal(int)
    send_showWin = pyqtSignal(int)

    def __init__(self, databaseName, source=0, threshold=1000, checkStranger=True):
        """
        初始化检测线程
        :param databaseName: 数据库文件名
        :param threshold: 数据库存储报警信息条数的阈值, 默认为1000
        """
        super(DetThread, self).__init__()
        self.source = source
        self.threshold = threshold  # 设置数据库存储报警信息条数的阈值, 超过这个阈值就开始删除老数据
        self.model = YOLO('./pt/best.pt')  # 这个先不改, 看看后面模型放哪先
        self.dataBaseName = databaseName
        self.save_folder = 'detect_results'
        os.makedirs(self.save_folder, exist_ok=True)
        self.frameCnt = 0
        self.frame_width = 400
        self.frame_height = 300
        self.checkingStranger = checkStranger
        self._initThreadDatabase()
        self._initSaveTime()

    def _initSaveTime(self):
        """
        初始化保存时间和计数器
        :return:
        """
        current_time = datetime.now()
        current_time_str = current_time.strftime("%Y%m%d")  # 将 current_time 转换为字符串形式，格式为年月日时分秒
        self.save_folder = os.path.join(self.save_folder, current_time_str)
        print('Current save_folder is {}!'.format(self.save_folder))
        os.makedirs(self.save_folder, exist_ok=True)
        # 初始化各类别的计数器和开始时间
        self.detThreshold = 2
        self.detThresholdEnd = 5
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
        # 由于视频打开时间有延迟, 所以(根据我的设备情况)设置一个偏移量
        self.delta = 3

    def _initThreadDatabase(self):
        """
        初始化线程数据库连接
        :return:
        """
        self.conn = sql.connect(os.path.join(self.dataBaseName),
                                isolation_level=None, uri=True, check_same_thread=False)
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*) FROM alarmRecord')
        self.curInsertID = c.fetchone()[0] + 1

    def run(self):
        """
        执行线程的运行逻辑, 处理视频帧并进行物体检测
        :return:
        """

        print('Enter RUN!')

        self.cap = cv2.VideoCapture(self.source)    # 打开视频源(摄像头)
        current_time = datetime.now()       # 获取当前时间
        current_time += timedelta(seconds=self.delta)       # 加上时间偏移量
        current_time_str = current_time.strftime("%Y-%m-%d_%H-%M-%S")  # 将 current_time 转换为字符串形式，格式为年月日时分秒
        self.video_filename = f"{current_time_str}.mp4"  # 使用 current_time_str 作为视频文件名的一部分

        # 视频帧计数器
        frame_count = 0

        # 视频帧宽高
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 视频帧写入对象
        self.out = cv2.VideoWriter(os.path.join(self.save_folder, self.video_filename), cv2.VideoWriter_fourcc(*'mp4v'),
                                   5,
                                   (self.frame_width, self.frame_height))
        self.startTime = time.time()    # 记录开始时间
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
                        # print('Enter if self.fire_start_time is not None and self.fire_locked:')
                        if self.fire_end_time is None:
                            self.fire_end_time = current_frame_time
                        if cls == 1:
                            # print(f'self.fire_end_count = {self.fire_end_count}')
                            self.fire_end_count += 1

                    if self.person_start_time is not None and self.person_locked:
                        # print('Enter if self.person_start_time is not None and self.person_locked:')
                        if self.person_end_time is None:
                            self.person_end_time = current_frame_time
                        if cls == 2:
                            # print(f'self.person_end_count = {self.person_end_count}')
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
                self.frameCnt += 1

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
        """
        检查并重置烟雾检测的开始时间
        :param current_time: 当前时间
        :return:
        """
        # 计算当前时间和最后一次记录时间的差值
        time_diff = (current_time - self.smoke_start_time).total_seconds() * 1000

        if time_diff >= 1000:  # 超过一秒
            if self.smoke_count < self.detThreshold:
                # 如果计数小于5，重置计数器和开始时间
                self.smoke_count = 0
                self.smoke_start_time = current_time
            else:
                # 如果计数大于等于5，锁定计数器和开始时间，停止计数
                self.smoke_locked = True  # 假设有一个 locked 属性用于锁定计数器
                print('警告！检测到烟雾！')
                self.send_showWin.emit(0)

    def check_reset_fire_start_time(self, current_time):
        """
        检查并重置火焰检测的开始时间
        :param current_time: 当前时间
        :return:
        """
        # 计算当前时间和最后一次记录时间的差值
        time_diff = (current_time - self.fire_start_time).total_seconds() * 1000

        if time_diff >= 1000:  # 超过一秒
            if self.fire_count < self.detThreshold:
                # 如果计数小于5，重置计数器和开始时间
                self.fire_count = 0
                self.fire_start_time = current_time
            else:
                # 如果计数大于等于5，锁定计数器和开始时间，停止计数
                self.fire_locked = True  # 假设有一个 locked 属性用于锁定计数器
                print('警告！检测到火焰！')
                self.send_showWin.emit(1)

    def check_reset_person_start_time(self, current_time):
        """
        检查并重置人物检测的开始时间
        :param current_time: 当前时间
        :return:
        """
        # 计算当前时间和最后一次记录时间的差值
        time_diff = (current_time - self.person_start_time).total_seconds() * 1000

        if time_diff >= 1000:  # 超过一秒
            if self.person_count < self.detThreshold:
                # 如果计数小于5，重置计数器和开始时间
                self.person_count = 0
                self.person_start_time = current_time
            else:
                # 如果计数大于等于5，锁定计数器和开始时间，停止计数
                self.person_locked = True  # 假设有一个 locked 属性用于锁定计数器
                if self.checkingStranger == True:
                    print('警告！检测到陌生人闯入！')
                    self.send_showWin.emit(2)

    def check_reset_end_time(self, current_time):
        """
        检查并重置结束时间
        :param current_time: 当前时间
        :return:
        """
        # print('Enter check_reset_end_time')
        # 添加结束时间处理逻辑
        if self.smoke_end_time is not None:
            if (current_time - self.smoke_end_time).total_seconds() * 1000 >= 1000:
                if self.smoke_end_count < self.detThresholdEnd:
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
            # print('Enter if self.fire_end_time is not None:')
            # print(f'current_time = {current_time}')
            # print(f'self.fire_end_time = {self.fire_end_time}')
            if (current_time - self.fire_end_time).total_seconds() * 1000 >= 1000:
                # print('Enter current_time - self.fire_end_time')
                # print(self.fire_end_count)
                if self.fire_end_count < self.detThresholdEnd:
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
            # print('Enter if self.person_end_time is not None:')
            # print(f'current_time = {current_time}')
            # print(f'self.person_end_time = {self.person_end_time}')
            if (current_time - self.person_end_time).total_seconds() * 1000 >= 1000:
                # print('Enter current_time - self.person_end_time')
                # print(self.person_end_count)
                if self.person_end_count < self.detThresholdEnd:
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
        """
        如果计数器超过阈值, 保存报警信息到数据库中
        :param start_count: 计数开始值
        :param end_count: 计数结束值
        :param start_time: 报警开始时间
        :param end_time: 报警结束时间
        :param cls: 报警类别
        :return: 报警信息保存成功与否的布尔值标志
        """
        # 如果计数器超过阈值
        # print('Enter save_if_threshold_exceeded!')
        if start_count > self.detThreshold and self.detThresholdEnd > end_count:
            start_time_str = start_time.strftime('%Y-%m-%d_%H-%M-%S')
            end_time_str = end_time.strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'{cls}_' + start_time_str + '__' + end_time_str + '.txt'
            # 构建文件路径
            filepath = os.path.join(self.save_folder, filename)
            # 保存开始时间和类别到文本文件
            self.saveTimestamp(start_time, end_time, filepath, cls)
            return True     # 返回报警信息保存成功的标志
        else:
            return False    # 返回报警信息保存失败的标志

    def saveTimestamp(self, start_time, end_time, filepath, cls):
        """
        将报警的开始时间, 结束时间和报警类别写入数据库
        :param start_time: 报警开始时间
        :param end_time: 报警结束时间
        :param filepath: 文件路径
        :param cls: 报警类别
        :return:
        """
        # 格式化开始时间和结束时间为字符串
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        print('Ready to write {}!'.format(filepath))
        if (cls == '0') or (cls == '1') or (cls == '2' and self.checkingStranger):
            c = self.conn.cursor()
            c.execute("INSERT INTO alarmRecord (id, startTime, endTime, alarmType, camNo) VALUES (?, ?, ?, ?, ?)",
                      (str(self.curInsertID), start_time_str, end_time_str, str(cls), str(self.source)))
            self.conn.commit()
            self.curInsertID += 1
            self.send_infoInsert.emit(self.curInsertID % self.threshold)
        # # 将时间戳写入文本文件
        # with open(filepath, 'w') as file:
        #     file.write('{} {} {}'.format(cls, start_time_str, end_time_str))

    def quit(self) -> None:
        """
        退出方法, 释放资源并保存视频
        :return:
        """
        # 释放视频和输出对象资源
        self.cap.release()
        self.out.release()

        # 根据设置的差值 delta 更新开始时间
        self.startTime += self.delta
        endTime = time.time()
        duration = endTime - self.startTime

        # 获取当前时间作为结束时间
        # averageFps = math.floor(self.frameCnt / duration)
        endTimeStr = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        time.sleep(2)

        # 构建原文件名
        filepath = os.path.join(self.save_folder, self.video_filename)

        # 如果文件存在
        if os.path.isfile(filepath):
            basename, extension = os.path.splitext(self.video_filename)
            # endTimeStr = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            new_name = f"{basename}_{endTimeStr}_{self.source}{extension}"
            new_file_path = os.path.join(self.save_folder, new_name)

            # 打开视频文件并计算平均帧率
            cap = cv2.VideoCapture(filepath)
            totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            averageFps = math.floor(totalFrames / duration)

            # 创建新的视频输出对象并复制帧
            out = cv2.VideoWriter(new_file_path, cv2.VideoWriter_fourcc(*'mp4v'), averageFps,
                                  (self.frame_width, self.frame_height))
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                else:
                    break
            cap.release()
            out.release()

            # 删除源文件
            os.remove(filepath)
            # os.rename(filepath, new_file_path)

        # 提交数据库操作并关闭连接
        self.conn.commit()
        self.conn.close()
        super().quit()  # 调用父类的退出方法


class MainWindow(QMainWindow):
    """
    主窗口类
    Attributes:
        ui: 主窗口的UI界面
        isMaxi: 当前窗口是否全屏的布尔值标志
        curInsertID: 当前(未)插入的最新数据库id位置
        threshold: 数据库报警信息插入条数阈值
        Datalist: 报警记录表格的数据容器变量
        alarmRowCount: 报警记录表格的设定最大行数
        totalLinesCnt: 当前获取到的报警条数
        searchRowCnt: 查看回放表格的设定最大行数
        videoFileSaveFolder: 保存视频回放文件的目录名
        SearchDatalist: 查看回放表格的数据容器变量
        UserDatalist: 用户信息表格的数据容器变量
    """
    ui = Ui_MainWindow()
    isMaxi = False

    # DetThread
    curInsertID = 0  # 这是当前(未)插入的最新数据库id位置    (满减逻辑未实现)
    threshold = 10000  # 数据库报警信息插入条数阈值

    # 这是PageTable实现的变量
    Datalist = [()]
    # RowIndex = 0
    # pageCount = 15

    alarmRowCount = 10
    totalLinesCnt = 0  # 当前获取到的报警条数

    ##############
    searchRowCnt = 10
    videoFileSaveFolder = 'detect_results'
    SearchDatalist = [[]]

    UserDatalist = [[]]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
        self._initUi()
        self._initPageTable()
        self._initVideoReplay()
        self._initDatabase()
        self._initDetThread()
        self._initVideoSearch()
        self._initUserPage()
        self.gotoBlock(0)

    def videoReplay(self, infoGroup):
        """
        视频回放功能
        根据传入的信息组infoGroup回放响应的视频, 此处有两个分支功能: 直接视频回放 与 根据报警记录跳转到指定位置回放视频
        这两者之间的判断依据为 - infoGroup中的 fileName 是否为空
        :param infoGroup: 包含视频回放所需信息的列表, 格式为 [startTime, endTime, camNo, fileName, btnNo]
        :return:
        """
        if len(infoGroup[-2]) != 0:
            # 获取视频文件的绝对路径
            absolute_path = os.path.join(self.videoFileSaveFolder, self.folderName,
                                         infoGroup[-2])
            self.rtPageIndex = 3
            # 打开视频文件
            if not self.openVideoFile(absolute_path):
                self.rtPageIndex = 0
                MessageBox(text='回放文件尚未生成或已被清理!', mode=0).exec_()
        else:
            # infoGroup = [self.startTime, self.endTime, self.camNo, self.fileName, self.btnNo]  格式: 2024-10-30 09:53:00
            # 解析报警开始的日期和时间
            dateFolder, alarmStartTime = str(infoGroup[0]).split(' ')
            dateFolder = str(dateFolder).split('-')
            dateFolder = dateFolder[0] + dateFolder[1] + dateFolder[2]
            alarmEndTime = str(infoGroup[1]).split(' ')[1]
            alarmStartTime = datetime.strptime(alarmStartTime, "%H:%M:%S")
            alarmDeltaStartTime = alarmStartTime + timedelta(seconds=3)
            alarmEndTime = datetime.strptime(alarmEndTime, "%H:%M:%S")
            data = os.path.join(self.videoFileSaveFolder, dateFolder)
            print('Path is ' + data)

            # 检查对应日期文件夹是否存在
            if os.path.exists(data):
                mp4Files, _ = self.get_mp4_files(data)
                findOne = False

                # 遍历对应日期文件夹下的所有视频文件
                for file in mp4Files:
                    basename, extension = os.path.splitext(file)
                    myTimeList = basename.split('_')
                    videoStartTime = datetime.strptime(myTimeList[1], "%H-%M-%S")
                    videoEndTime = datetime.strptime(myTimeList[3], "%H-%M-%S")

                    # 判断报警事件是否在视频时间范围内
                    if videoStartTime.time() <= alarmStartTime.time() <= alarmEndTime.time() <= videoEndTime.time() \
                            or videoStartTime.time() <= alarmDeltaStartTime.time() <= alarmEndTime.time() <= videoEndTime.time():
                        findOne = True
                        jumpSec = int((alarmStartTime - videoStartTime).total_seconds())
                        self.rtPageIndex = 1
                        # 打开对应的视频文件
                        if not self.openVideoFile(os.path.join(data, file), jumpSec):
                            self.rtPageIndex = 0
                            MessageBox(text='回放文件尚未生成或已被清理!', mode=0).exec_()
                        break
                if not findOne:
                    self.rtPageIndex = 0
                    MessageBox(text='回放文件尚未生成或已被清理!', mode=0).exec_()
            else:
                self.rtPageIndex = 0
                MessageBox(text='回放文件尚未生成或已被清理!', mode=0).exec_()

    def myClose(self):
        """
        关闭窗口功能
        关闭程序前进行必要的操作, 如退出检测线程, 提交数据库事务等
        :return:
        """
        # 退出检测线程
        if self.detThreadAlive:
            self.detThread.quit()

        # 提示正在关闭程序
        MessageBox(text='正在关闭程序...', auto=True, time=2000, mode=2, iconpath=':/home/icon/bye.png').exec_()

        # 提交数据库事务并关闭连接
        self.conn.commit()  # 这里提交用户账号信息的修改, 防止出现同时写的报错和不一致情况
        self.conn.close()

        # 关闭窗口
        self.close()

    def gotoBlock(self, index: int):
        """
        跳转到指定页面的功能
        根据传入的索引值跳转到对应的页面, 并执行响应的初始化操作
        :param index: 要跳转的页面索引值
        :return:
        """
        # 设置跳转之后的初始刷新, 如果没有就会导致页面显示混乱
        if index == 1:
            self.ui.page1Button.setChecked(False)
            self.ui.page2Button.setChecked(True)
            self.ui.page4Button.setChecked(False)
            self.ui.page5Button.setChecked(False)
            self.BtnLoadDataClick()
        elif index == 3:
            self.ui.page1Button.setChecked(False)
            self.ui.page2Button.setChecked(False)
            self.ui.page4Button.setChecked(True)
            self.ui.page5Button.setChecked(False)
            self.BtnQureyClick()
        elif index == 4:
            self.ui.page1Button.setChecked(False)
            self.ui.page2Button.setChecked(False)
            self.ui.page4Button.setChecked(False)
            self.ui.page5Button.setChecked(True)
            self.updateUserPage()
        elif index == 0:
            self.ui.page1Button.setChecked(True)
            self.ui.page2Button.setChecked(False)
            self.ui.page4Button.setChecked(False)
            self.ui.page5Button.setChecked(False)
        elif index == 2:
            self.speedMode = 3
            self.changeSpeed()

        # 设置当前页面索引
        self.ui.stackedWidget.setCurrentIndex(index)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        鼠标移动事件
        根据鼠标位置改变光标形状, 实现窗口的移动和调整大小功能
        :param event: 鼠标事件对象
        :return:
        """
        # print('Enter MouseMoveEvent!')
        # 定义窗口边界区域
        self.right_edge = QRect(self.width() - 10, 0, self.width(), self.height())
        self.bottom_edge = QRect(0, self.height() - 20, self.width() - 25, self.height())
        self.right_bottom_edge = QRect(self.width() - 25, self.height() - 10, self.width(), self.height())
        self.windowRange = QRect(0, 0, self.width() - 25, self.height() - 20)

        # 判断鼠标位置并设置光标形状
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
        """
        鼠标释放事件
        标记鼠标释放的状态
        :param event: 鼠标事件对象
        :return:
        """
        self.m_flag = False

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        鼠标按下事件
        标记鼠标按下状态, 并实现窗口的移动和调整大小功能
        :param event: 鼠标事件对象
        :return:
        """
        # 记录鼠标位置
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
        """
        事件过滤器
        过滤鼠标进入事件, 重置光标形状
        :param obj: 事件对象
        :param event: 事件类型
        :return: 事件处理结果
        """
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
            self.direction = None
        return super().eventFilter(obj, event)

    def onTitleBarDoubleClicked(self, event: QMouseEvent):
        """
        标题栏双击事件处理方法
        :param event: 鼠标事件对象
        :return:
        """
        if event.buttons() == Qt.LeftButton:
            self.maxOrRestore()

    def maxOrRestore(self):
        """
        最大化/还原窗口方法
        根据窗口当前的状态执行最大化或还原操作, 并更新按钮状态
        :return:
        """
        if not self.isMaxi:
            self.showMaximized()
            self.isMaxi = True
            self.ui.maxiButton.setChecked(True)
        else:
            self.showNormal()
            self.isMaxi = False
            self.ui.maxiButton.setChecked(False)

    def LoadPage(self, pageIndex: int):
        """
        加载报警记录页面数据方法
        根据指定页面索引加载对应的数据
        :param pageIndex: 页面索引值
        :return:
        """
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

        self.pageTable.SetData(self.Datalist, dataType=0)

    def BtnLoadDataClick(self):
        """
        加载数据按钮点击事件处理方法
        加载数据并更新报警记录页面
        :return:
        """
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
        """
        页面切换事件处理方法
        :param currentPage: 当前页码
        :return:
        """
        self.LoadPage(currentPage)

    # VideoReplay
    def volumnChange(self, position):
        """
        调节声音组件的滑块改变的时间处理方法
        根据滑块位置改变视频播放的音量, 并更新音量显示
        :param position: 滑块位置
        :return:
        """
        volume = round(position / self.ui.sld_audio.maximum() * 100)
        # print("volume %f" % volume)
        self.player.setVolume(volume)
        self.ui.lab_audio.setText("volume:" + str(volume) + "%")

    def clickedSlider(self, position):
        """
        点击进度条的事件处理方法
        根据进度条点击位置改变视频播放的位置, 并更新视频显示时间
        :param position: 点击位置
        :return:
        """
        if self.player.duration() > 0:
            # 计算视频当前播放的时间位置（以秒为单位）
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            # 将视频当前播放的时间位置转换为时间格式（小时:分钟:秒）
            hours, remainder = divmod(video_position / 1000, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = "%02d:%02d:%02d" % (hours, minutes, seconds)
            # 设置 lab_video 的文本为时间格式
            self.ui.lab_video.setText(time_format)
        else:
            self.ui.sld_video.setValue(0)

    def moveSlider(self, position):
        """
        进度条滑块移动事件处理方法
        根据进度条滑块移动的位置改变视频播放的位置, 并更新视频显示时间
        :param position: 滑块当前位置
        :return:
        """
        self.sld_video_pressed = True
        if self.player.duration() > 0:
            # video_position = int((position / 100) * self.player.duration())
            # self.player.setPosition(video_position)
            # self.ui.lab_video.setText("%.2f%%" % position)
            # 计算视频当前播放的时间位置（以秒为单位）
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            # 将视频当前播放的时间位置转换为时间格式（小时:分钟:秒）
            hours, remainder = divmod(video_position / 1000, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = "%02d:%02d:%02d" % (hours, minutes, seconds)
            # 设置 lab_video 的文本为时间格式
            self.ui.lab_video.setText(time_format)

    def pressSlider(self):
        """
        进度条按下事件处理方法
        标记进度条滑块被按下
        :return:
        """
        self.sld_video_pressed = True
        print("pressed")

    def releaseSlider(self):
        """
        进度条释放事件处理方法
        标记进度条滑块被释放
        :return:
        """
        self.sld_video_pressed = False

    def changeSlider(self, position):
        """
        拖动进度条改变位置的事件处理犯法
        根据进度条的值改变视频播放的位置, 并更新显示事件
        :param position: 进度条的当前值
        :return:
        """
        if not self.sld_video_pressed:
            self.videoLength = self.player.duration() + 0.1
            self.ui.sld_video.setValue(round((position / self.videoLength) * 100))
            # 计算视频当前播放的时间位置（以秒为单位）
            video_position = int(position)
            # 将视频当前播放的时间位置转换为时间格式（小时:分钟:秒）
            hours, remainder = divmod(video_position / 1000, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = "%02d:%02d:%02d" % (hours, minutes, seconds)
            # 设置 lab_video 的文本为时间格式
            self.ui.lab_video.setText(time_format)

    def openVideoFile(self, absolutePath: str, jumpSec=0) -> bool:
        """
        打开视频文件的方法
        根据给定的视频文件路径打开视频文件, 并跳转到指定位置
        :param absolutePath: 视频文件的绝对路径
        :param jumpSec: 跳转的秒数, 默认为 0
        :return: 是否成功打开视频文件
        """
        if os.path.isfile(absolutePath):
            self.gotoBlock(2)
            mediaContent = QMediaContent(QUrl.fromLocalFile(absolutePath))
            self.player.setMedia(mediaContent)  # 选取视频文件
            if jumpSec != 0:
                self.player.setPosition(int(jumpSec * 1000))
            self.player.play()
            return True
        else:
            return False

    def playVideo(self):
        """
        播放/暂停视频方法
        根据按钮状态控制视频的播放或暂停
        :return:
        """
        if self.ui.btn_play.isChecked():
            self.player.pause()
        else:
            self.player.play()

    def stopVideo(self):
        """
        停止视频播放方法
        停止视频的播放
        :return:
        """
        self.player.stop()

    def _initUi(self):
        """
        初始化界面
        设置窗口标志, 按钮功能以及鼠标跟踪
        :return:
        """
        # Ui
        # 设置窗口标志和按钮功能
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
        # self.ui.page3Button.clicked.connect(lambda: self.gotoBlock(2))
        self.ui.page4Button.clicked.connect(lambda: self.gotoBlock(3))
        self.ui.page5Button.clicked.connect(lambda: self.gotoBlock(4))
        self.ui.CameraButton.clicked.connect(self.choose_cam)
        self.ui.titleGroupBox.mouseDoubleClickEvent = self.onTitleBarDoubleClicked

        # 设置鼠标跟踪
        self.setMouseTracking(True)
        self.ui.centralwidget.setMouseTracking(True)
        self.ui.titleGroupBox.setMouseTracking(True)
        self.ui.frame.setMouseTracking(True)
        self.ui.frame_2.setMouseTracking(True)
        self.ui.frame_3.setMouseTracking(True)
        self.ui.closeButton.setMouseTracking(True)
        self.ui.maxiButton.setMouseTracking(True)
        self.ui.miniButton.setMouseTracking(True)
        # self.ui.groupBox.installEventFilter(self)
        # self.ui.frame.installEventFilter(self)
        self.ui.stackedWidget.installEventFilter(self)
        self.m_flag = False
        self.direction = None
        # pixmap = QPixmap(':/login/icon/applabel.png')
        # pixmap.scaled(250, 25)
        # self.ui.softwareNameLabel.setPixmap(pixmap)

    def _initDatabase(self):
        """
        初始化数据库连接和数据表
        :return:
        """
        self.dataBaseName = 'myDB.db'
        self.conn = sql.connect(os.path.join(self.dataBaseName),
                                isolation_level=None, uri=True, check_same_thread=False)  # 启用WAL模式
        c = self.conn.cursor()
        # 如果不存在 alarmRecord 表, 则进行创建
        c.execute('''CREATE TABLE IF NOT EXISTS alarmRecord 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                    startTime TEXT NOT NULL, 
                    endTime TEXT NOT NULL, 
                    alarmType INTEGER NOT NULL, 
                    camNo INTEGER NOT NULL)
        ''')
        self.conn.commit()

    def _initPageTable(self):
        """
        初始化报警记录表格
        :return:
        """
        # 初始化表头和表格
        # PageTable
        header = ["序号", "开始时间", "结束时间", "报警类型", "摄像头编号", "操作"]
        self.pageTable = PageTable(header, self.alarmRowCount)
        self.ui.testLayout.addLayout(self.pageTable)
        self.pageTable.pageWidget.send_curPage.connect(lambda x: self.PageChange(x))
        self.pageTable.tableWidget.setShowGrid(False)
        # self.pageTable.tableWidget.horizontalHeader().setDefaultSectionSize(50)
        self.pageTable.tableWidget.verticalHeader().setDefaultSectionSize(40)
        self.ui.btnLoadData.clicked.connect(self.BtnLoadDataClick)

        # 设置表格按钮
        self.pageButtons = []
        for i in range(self.alarmRowCount):
            button = PageButton()
            button.btnNo = i + 1
            # button.setText('回 放')
            button.send_myNo.connect(lambda x: self.videoReplay(x))
            icon = QIcon(':/home/icon/arrow-right.png')
            button.setIcon(icon)
            button.setIconSize(QSize(20, 20))
            button.setStyleSheet('''QPushButton {
                background: transparent;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {background-color: rgb(222, 222, 222);}
            QPushButton:pressed {background-color: rgb(189, 189, 189);}
            ''')
            self.pageButtons.append(button)

    def _initVideoSearch(self):
        """
        初始化视频回放表格
        :return:
        """
        # 设置日期编辑框
        self.ui.dateEdit.setDate(QDate.currentDate())

        # 初始化表头和表格
        header = ["序号", "录像名称", "开始时间", "结束时间", "摄像头编号", "文件大小(MB)", "操作"]
        self.searchTable = PageTable(header, self.searchRowCnt)
        self.ui.searchLayout.addLayout(self.searchTable)
        self.searchTable.pageWidget.send_curPage.connect(lambda x: self.searchPageChange(x))
        self.ui.queryButton.clicked.connect(self.BtnQureyClick)
        self.searchTable.tableWidget.setShowGrid(False)
        self.searchTable.tableWidget.verticalHeader().setDefaultSectionSize(40)

        # 设置表格按钮
        self.searchPageButtons = []
        for i in range(self.searchRowCnt):
            button = PageButton()
            button.btnNo = i + 1
            button.send_myNo.connect(lambda x: self.videoReplay(x))
            icon = QIcon(':/home/icon/arrow-right.png')
            button.setIcon(icon)
            button.setIconSize(QSize(20, 20))
            button.setStyleSheet('''QPushButton {
                background: transparent;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {background-color: rgb(222, 222, 222);}
            QPushButton:pressed {background-color: rgb(189, 189, 189);}
            ''')
            self.searchPageButtons.append(button)

    def searchPageChange(self, currentPage: int):
        """
        视频回放页面切换事件处理方法
        :param currentPage: 当前页码
        :return:
        """
        self.LoadSearchPage(currentPage)

    def LoadSearchPage(self, currentPage: int):
        """
        加载视频回放页面的方法
        根据当前页码加载视频回放页面的数据
        :param currentPage: 当前页码
        :return:
        """
        self.SearchDatalist.clear()     # 清空数据列表

        # 计算边界索引
        leftBorfer = (currentPage - 1) * self.searchRowCnt
        rightBorder = currentPage * self.searchRowCnt

        # 检查右边界是否超出文件列表长度
        if currentPage * self.searchRowCnt > len(self.mp4Files):
            rightBorder = len(self.mp4Files)

        # 遍历数据范围内的索引, 给对应行的 button 填充当前行的相关信息以便后续点击跳转回放
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

        # 更新表格
        self.searchTable.SetData(self.SearchDatalist, dataType=1)

    def BtnQureyClick(self):
        """
        视频查询按钮点击事件处理方法
        根据日期查询视频回放文件
        :return:
        """
        # 获取QDateEdit里面的内容, 然后根据它去查找视频回放 (定义好文件夹和视频的保存路径以及文件名称
        selected_date = self.ui.dateEdit.date()
        # print("Selected Date: ", selected_date.toString("yyyy-MM-dd"))
        self.folderName = selected_date.toString("yyyyMMdd")
        # print(folderName)
        if os.path.exists(os.path.join(self.videoFileSaveFolder, self.folderName)):
            self.mp4Files, self.fileSizes = self.get_mp4_files(
                os.path.join(self.videoFileSaveFolder, self.folderName))
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
            MessageBox(text='暂无可查看回放!', mode=0).exec_()
            # QMessageBox.information(self, '', '暂无可查看回放！')
            return

    def get_mp4_files(self, directory):
        """
        获取指定目录下的mp4文件列表的方法
        :param directory: 目录路径
        :return: mp4文件列表
        """
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
        """
        提取文件名中的时间戳和摄像头编号
        :param filename: 文件名
        :return: 时间戳列表(视频开始时间 + 视频结束时间)和摄像头编号组成的元组
        """
        # 定义日期时间格式的正则表达式模式
        pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
        # 在文件名中搜索匹配的日期时间字符串
        timestamps = re.findall(pattern, filename)
        parts = filename.split('_')
        camereNumber = parts[-1].split('.')[0]
        return timestamps, camereNumber

    def transform_timestamp(self, timestamp):
        """
        转换时间戳格式的方法
        :param timestamp: 时间戳字符串
        :return: 转换后的时间戳字符串
        """
        stamplist = timestamp.split('_')
        # 将时间戳中的 '_' 替换为 ' '，将 '-' 替换为 ':'，得到新的格式
        transformed_timestamp = stamplist[-1].replace('-', ':')
        timestamp_new = stamplist[0] + ' ' + transformed_timestamp
        return timestamp_new

    def choose_cam(self):
        # 断开连接检测线程的信号与槽并关闭原来的检测线程
        if self.detThreadAlive:
            self.detThread.quit()
            self.detThreadAlive = False
        MessageBox(text='正在搜索摄像头...', mode=2, auto=True,
                   time=2000, iconpath=':/home/icon/Camera.png').exec_()

        _, cams = Camera().get_cam_num()
        popMenu = QMenu()
        popMenu.setFixedWidth(self.ui.CameraButton.width())
        popMenu.setStyleSheet('''
                                        QMenu {
                                        font-size: 16px;
                                        font-family: "Microsoft YaHei UI";
                                        font-weight: light;
                                        color:white;
                                        padding-left: 5px;
                                        padding-right: 5px;
                                        padding-top: 4px;
                                        padding-bottom: 4px;
                                        border-style: solid;
                                        border-width: 0px;
                                        border-color: rgba(255, 255, 255, 255);
                                        border-radius: 3px;
                                        background-color: rgba(200, 200, 200,50);}
                                        ''')
        for cam in cams:
            exec("action_%s = QAction('%s')" % (cam, cam))
            exec("popMenu.addAction(action_%s)" % cam)
        x = self.ui.titleGroupBox.mapToGlobal(self.ui.CameraButton.pos()).x()
        y = self.ui.titleGroupBox.mapToGlobal(self.ui.CameraButton.pos()).y()
        y = y + self.ui.CameraButton.frameGeometry().height()
        pos = QPoint(x, y)
        action = popMenu.exec_(pos)
        if action:
            self.detThread = DetThread(self.dataBaseName, int(action.text()), self.threshold, self.checkStranger)
            self.detThreadAlive = True
            # 连接检测线程的信号与槽
            self.detThread.send_img.connect(lambda x: self.show_video(x, self.ui.out_video))
            self.detThread.send_infoInsert.connect(lambda x: self.updateCurInsertID(x))
            self.detThread.send_showWin.connect(lambda x: self.showAlarmWindow(x))

            # 启动检测线程
            self.detThread.start()

    def _initDetThread(self):
        """
        初始化检测线程
        设置检测线程并连接信号和槽
        :return:
        """
        # detThread
        # 初始化检测线程
        _, cams = Camera().get_cam_num()
        if len(cams) == 0:
            # 如果未找到可用摄像头，则关闭程序
            MessageBox(text='未找到可用摄像头, 正在关闭程序...', auto=True, time=2000, mode=2, iconpath=':/home/icon/bye.png').exec_()

            # 提交数据库事务并关闭连接
            self.conn.commit()
            self.conn.close()

            # 关闭窗口
            self.close()
            sys.exit()
        self.checkStranger = True
        self.detThread = DetThread(self.dataBaseName, cams[0], self.threshold, self.checkStranger)
        self.detThreadAlive = True

        # 连接检测线程的信号与槽
        self.detThread.send_img.connect(lambda x: self.show_video(x, self.ui.out_video))
        self.detThread.send_infoInsert.connect(lambda x: self.updateCurInsertID(x))
        self.detThread.send_showWin.connect(lambda x: self.showAlarmWindow(x))
        self.ui.StrangerButton.clicked.connect(self.changeMode)

        # 启动检测线程
        self.detThread.start()

    def showAlarmWindow(self, cls: int):
        """
        显示警报窗口, 根据传入的警报类型显示响应的警报信息
        :param cls: 警报类型, 0表示烟雾, 1表示火焰, 2表示陌生人员闯入
        :return:admin
        """
        if cls == 0:
            msgBox = MessageBox(text='警告！检测到烟雾！', iconpath=':/home/icon/alarm.png', mode=3).exec_()
        elif cls == 1:
            msgBox = MessageBox(text='警告！检测到火焰！', iconpath=':/home/icon/alarm.png', mode=3).exec_()
        elif cls == 2:
            msgBox = MessageBox(text='警告！检测到陌生人员闯入！', iconpath=':/home/icon/alarm.png', mode=3).exec_()

    def changeMode(self):
        """
        根据用户是否选择开启陌生人识别功能, 改变检测线程的识别模式
        :return:
        """
        if self.ui.StrangerButton.isChecked():
            print("开启陌生人识别")
            self.ui.StrangerButton.setText("关闭陌生人识别")
            if self.detThreadAlive:
                self.detThread.checkingStranger = True
            self.checkStranger = True
        else:
            self.ui.StrangerButton.setText("开启陌生人识别")
            print("关闭陌生人识别")
            if self.detThreadAlive:
                self.detThread.checkingStranger = False
            self.checkStranger = False

    def _initVideoReplay(self):
        """
        初始化视频播放页面
        设置视频播放器, 按钮和进度条功能
        :return:
        """
        # VideoReplay
        # 初始化视频播放器
        self.sld_video_pressed = False
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.ui.wgt_video)

        # 连接视频播放器的信号与槽
        self.ui.btn_play.clicked.connect(self.playVideo)
        self.ui.btn_stop.clicked.connect(self.stopVideo)
        self.player.positionChanged.connect(self.changeSlider)
        self.ui.sld_video.setTracking(False)
        self.ui.sld_video.sliderReleased.connect(self.releaseSlider)
        self.ui.sld_video.sliderPressed.connect(self.pressSlider)
        self.ui.sld_video.sliderMoved.connect(self.moveSlider)
        self.ui.sld_video.ClickedValue.connect(self.clickedSlider)
        self.ui.sld_audio.valueChanged.connect(self.volumnChange)
        self.rtPageIndex = 0  # 返回的页面下标
        self.ui.returnBtn.clicked.connect(self.rtBlock)
        self.speedMode = 0  # 0是1倍速, 1是1.25倍速, 2是1.5倍速, 3是2倍速
        self.ui.zoomBtn.clicked.connect(self.changeSpeed)

    def changeSpeed(self):
        """
        根据当前视频播放速度循环切换不同的播放速度(1.0->1.25->1.5->2.0->1.0->...)
        :return:
        """
        self.speedMode = (self.speedMode + 1) % 4
        if self.speedMode == 0:
            self.ui.zoomBtn.setText('1.0×')
            self.player.setPlaybackRate(1.0)
        elif self.speedMode == 1:
            self.ui.zoomBtn.setText('1.25×')
            self.player.setPlaybackRate(1.25)
        elif self.speedMode == 2:
            self.ui.zoomBtn.setText('1.5×')
            self.player.setPlaybackRate(1.5)
        else:
            self.ui.zoomBtn.setText('2.0×')
            self.player.setPlaybackRate(2.0)

    def rtBlock(self):
        """
        在视频播放页面点击返回按钮后跳转回到之前页面的方法
        :return:
        """
        self.player.stop()
        self.ui.btn_play.setChecked(False)
        self.gotoBlock(self.rtPageIndex)

    def updateCurInsertID(self, id: int):
        """
        根据传入的id值更新当前插入的ID
        :param id:
        :return:
        """
        self.curInsertID = id

    def _initUserPage(self):
        """
        初始化用户信息页面
        设置用户信息表格和添加用户按钮功能
        :return:
        """
        # 连接添加用户按钮的功能方法
        self.ui.userAddBtn.clicked.connect(self.addUser)

        # 初始化用户信息表格
        self.userpageRowCnt = 8
        header = ["序号", "用户名", "密码", "操作"]
        self.userTable = PageTable(header, self.userpageRowCnt)
        self.ui.userLayout.addLayout(self.userTable)
        self.userTable.pageWidget.send_curPage.connect(lambda x: self.userPageChange(x))
        self.userTable.tableWidget.setShowGrid(False)
        self.userTable.tableWidget.verticalHeader().setDefaultSectionSize(40)

        # 设置用户信息表格按钮
        self.userPageButtons = []
        for i in range(self.userpageRowCnt):
            button = UserDelButton()
            button.btnNo = i + 1
            icon = QIcon(':/home/icon/people-delete.png')
            button.setIcon(icon)
            button.setIconSize(QSize(25, 25))
            button.send_myNo.connect(lambda x: self.deleteUser(x))
            button.setStyleSheet('''QPushButton {
                background: transparent;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {background-color: rgb(222, 222, 222);}
            QPushButton:pressed {background-color: rgb(189, 189, 189);}
            ''')
            self.userPageButtons.append(button)

    def userPageChange(self, currenPage: int):
        """
        根据当前页码切换用户信息页面, 并加载相应的用户数据
        :param currenPage: 当前页码
        :return:
        """
        self.LoadUserPage(currenPage)

    def LoadUserPage(self, currentPage: int):
        """
        加载用户信息页面数据, 填充用户信息表格
        :param currentPage: 当前页码
        :return:
        """
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
        self.userTable.SetData(self.UserDatalist, dataType=2)

    def updateUserPage(self):
        """
        更新用户页面
        查询用户信息总数, 设置用户表格的最大页数, 并加载第一页的用户数据
        :return:
        """
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM userInfo")
        self.totalUserCnt = c.fetchone()[0]
        self.userTable.pageWidget.setMaxPage(math.ceil(self.totalUserCnt / self.userpageRowCnt))
        self.userTable.pageWidget.setCurrentPage(1, True)
        self.LoadUserPage(1)

    def deleteUser(self, infoGroup):
        """
        删除用户的方法
        删除指定用户, 并更新用户页面数据
        :param infoGroup: 包含用户信息的元组
        :return:
        """
        # 如果当前数据库中仅剩 1 个用户的信息, 提示无法删除
        if self.totalUserCnt == 1:
            MessageBox(text='无法删除唯一的用户!', mode=0).exec_()
        else:
            msgBox = MessageBox(text='确定要删除该用户吗?', mode=1, iconpath=':/home/icon/people-delete-white.png')
            response = msgBox.exec_()
            if response == QMessageBox.Yes:
                userID = infoGroup[0]
                c = self.conn.cursor()
                c.execute('DELETE FROM userInfo WHERE userID = ?', (userID,))
                self.conn.commit()
                self.updateUserPage()

    def addUser(self):
        """
        添加用户的方法
        打开用户注册对话框, 添加新用户并更新用户信息页面数据
        :return:
        """
        self.regisDialog = registerDialog(firstIn=False)
        self.regisDialog.exec_()
        self.updateUserPage()

    # 628×471
    @staticmethod
    def show_video(img_src, label):
        """
        显示视频的方法
        根据视频源和标签对象, 显示视频
        :param img_src: 视频源
        :param label: 标签对象
        :return:
        """
        try:
            # 获取视频帧图像的高度, 宽度和通道数
            ih, iw, _ = img_src.shape
            # 获取标签对象的宽度和高度
            w = label.geometry().width()
            h = label.geometry().height()

            # 保持原始宽高比
            if iw / w > ih / h:
                # 计算缩放比例
                scal = w / iw
                # 计算新的宽度和高度
                nw = w
                nh = int(scal * ih)
                # 使用OpenCV进行图像缩放
                img_src_ = cv2.resize(img_src, (nw, nh))
                # print(f'宽: {nw} 高: {nh}')

            else:
                # 计算缩放比例
                scal = h / ih
                # 计算新的宽度和高度
                nw = int(scal * iw)
                nh = h
                # 使用OpenCV进行图像缩放
                img_src_ = cv2.resize(img_src, (nw, nh))
                # print(f'宽: {nw} 高: {nh}')

            # 将图像从BGR颜色空间转换为RGB颜色控件
            frame = cv2.cvtColor(img_src_, cv2.COLOR_BGR2RGB)
            # 创建PyQt5图像对象
            img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[2] * frame.shape[1],
                         QImage.Format_RGB888)
            # 在标签上设置图像
            label.setPixmap(QPixmap.fromImage(img))

        except Exception as e:
            print(repr(e))


class registerDialog(QDialog):
    """
    注册对话框类, 用于处理用户注册功能
    Attributes:
        abnormalExit: 用于标记程序是否非正常退出
        ui: 注册对话框的UI界面
        userNameValidator: 用户名输入验证器
        userPasswordValidator: 用户密码输入验证器
    """
    abnormalExit = False  # 用于给程序知道是非正常退出，可以不用展示后面的界面
    ui = Ui_newUserDialog()
    userNameValidator = LineEditValidator(
        fullPatterns=['', r'^[a-zA-Z0-9]{6,12}$'],  # 完整匹配模式
        partialPatterns=['', r'^[a-zA-Z0-9]{1,12}$'],   # 部分匹配模式
        fixupString=''
    )
    userPasswordValidator = LineEditValidator(
        fullPatterns=['', r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z0-9]{8,16}$'],    # 完整匹配模式
        partialPatterns=['', r'^[a-zA-Z0-9]{1,16}$'],   # 部分匹配模式
        fixupString=''
    )

    def __init__(self, firstIn=True, parent=None):
        """
        初始化注册对话框
        :param firstIn: 是否首次登录
        :param parent: 父窗口部件, 默认为None
        """
        super().__init__(parent)
        self.setFixedSize(480, 550)     # 设置对话框固定大小
        self.ui.setupUi(self)   # 设置注册界面UI
        self.setWindowFlag(Qt.FramelessWindowHint)  # 设置无边框窗口
        self.setAttribute(Qt.WA_TranslucentBackground)      # 设置背景透明

        # 连接按钮点击事件与槽函数
        self.ui.regisMiniButton.clicked.connect(self.showMinimized)     # 最小化按钮
        self.ui.regisCloseButton.clicked.connect(self.reject)  # 这里要设置让后面的东西别出来了    关闭按钮
        self.ui.userNameEdit.setValidator(self.userNameValidator)   # 用户名输入框设置验证器
        self.ui.userNameEdit.installEventFilter(self.userNameValidator)     # 安装事件过滤器
        # self.ui.userNameEdit.setPlaceholderText('6-12个英文/数字组合')
        self.ui.passwordEdit.setEchoMode(QLineEdit.Password)        # 设置密码输入框为密码模式
        self.ui.passwordEdit.setValidator(self.userPasswordValidator)   # 密码输入框设置验证器
        self.ui.passwordEdit.installEventFilter(self.userPasswordValidator)     # 安装事件过滤器
        # self.ui.passwordEdit.setPlaceholderText('8-16个英文/数字组合(至少一个英文大小写加数字)')
        self.ui.passwordConfirmEdit.setValidator(self.userPasswordValidator)    # 确认密码输入框设置验证器
        self.ui.passwordConfirmEdit.installEventFilter(self.userPasswordValidator)  # 安装事件过滤器
        self.ui.passwordConfirmEdit.setEchoMode(QLineEdit.Password)     # 设置确认密码输入框为密码模式
        # self.ui.passwordConfirmEdit.setPlaceholderText('与第一次的输入保持一致')
        self.ui.registerButton.clicked.connect(self.register)   # 注册按钮点击事件

        self.dataBaseName = 'myDB.db'   # 数据库文件名
        self.conn = sql.connect(self.dataBaseName, isolation_level=None, uri=True)  # 连接数据库, 启用WAL模式

        self.firstIn = firstIn  # 是否第一次进入系统标志
        # 如果是第一次登录, 显示首次登录提示
        if firstIn:
            MessageBox(time=3000, text='首次登录，请先创建用户!',
                       mode=2, iconpath=':/home/icon/add-mode.png', auto=True).exec_()

    def register(self):
        """
        处理注册按钮点击事件, 执行用户注册逻辑
        :return:
        """
        userInput_Name = self.ui.userNameEdit.text()    # 获取用户输入的用户名
        userInput_Password = self.ui.passwordEdit.text()        # 获取用户输入的密码
        userInput_PasswordConfirm = self.ui.passwordConfirmEdit.text()      # 获取用户输入的确认密码

        # 查询数据库中是否有重复的用户
        c = self.conn.cursor()
        c.execute('SELECT userID FROM userInfo')
        rows = c.fetchall()  # [('admin1',), ('admin2',)...]
        for row in rows:
            # 如果用户输入的注册用户名与数据库中的用户名重复, 弹出提示并清空输入框
            if userInput_Name == row[0]:
                MessageBox(text='用户名不能重复!', mode=0).exec_()
                self.ui.userNameEdit.clear()
                self.ui.passwordEdit.clear()
                self.ui.passwordConfirmEdit.clear()
                self.ui.userNameEdit.setFocus()
                return

        # 如果有任一输入框为空, 弹出提示
        if len(userInput_Name) == 0 or len(userInput_Password) == 0 or len(userInput_PasswordConfirm) == 0:
            MessageBox(text='用户名/密码不能为空!', mode=0).exec_()
            self.ui.userNameEdit.setFocus()
            return

        # 如果两次输入的密码不一致, 弹出提示
        if userInput_Password != userInput_PasswordConfirm:
            MessageBox(text='两次输入的密码不一致!', mode=0).exec_()
            self.ui.passwordEdit.clear()
            self.ui.passwordConfirmEdit.clear()
            self.ui.passwordEdit.setFocus()
            return

        # 经过上面的检测, 确认输入信息没问题, 将其写入数据库(密码经过加密后写入)
        c = self.conn.cursor()
        # userID = func_encrypt_config(key, userInput_Name)
        userCode = func_encrypt_config(key, userInput_Password)
        c.execute('INSERT INTO userInfo (userID, userCode) VALUES (?, ?)', (userInput_Name, userCode))

        # 如果是首次进入系统, 则跳转登陆界面, 否则为应用中的注册用户按钮弹出窗口, 直接结束即可
        if self.firstIn:
            MessageBox(text='注册成功!\n即将转到登陆界面...', mode=2, auto=True,
                       time=2000, iconpath=':/home/icon/good-two.png').exec_()
        else:
            MessageBox(text='注册成功!', mode=2, auto=True, time=1000, iconpath=':/home/icon/good-two.png').exec_()

        # 释放数据库资源
        self.conn.close()
        self.accept()


class loginDialog(QDialog):
    """
    登录对话框类, 用于处理用户的登录功能
    Attributes:
        ui: 登录对话框的UI界面
    """
    ui = Ui_Dialog()

    def __init__(self, parent=None):
        """
        初始化logiinDialog类的对象
        :param parent: 父窗口部件, 默认为None
        """
        super().__init__(parent)
        self.setFixedSize(480, 550)     # 设置对话框的固定大小
        self.ui.setupUi(self)       # 设置UI
        self.setWindowFlag(Qt.FramelessWindowHint)          # 去掉窗口边框
        self.setAttribute(Qt.WA_TranslucentBackground)      # 设置窗口背景透明
        self.ui.loginButton.clicked.connect(self.check)     # 连接登录按钮点击事件到 check 方法
        self.ui.loginMiniButton.clicked.connect(self.showMinimized)  # 连接最小化按钮点击事件到 showMinimized 方法
        self.ui.loginCloseButton.clicked.connect(self.reject)  # 连接关闭按钮点击事件到 reject 方法
        # self.ui.loginCloseButton.clicked.connect(self.close)
        self.ui.passwordEdit.setEchoMode(QLineEdit.Password)  # 设置密码输入框显示模式为密码模式
        self.tryLoginTimes = 4  # 初始化尝试登录次数 为4-1=3次
        self.dataBaseName = 'myDB.db'  # 数据库文件名
        self.conn = sql.connect(self.dataBaseName, isolation_level=None, uri=True)

        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        print(f"Screen Resolution: {screen_width}x{screen_height}")

        # pixmap = QPixmap(':/login/icon/applabel.png')
        # pixmap.scaled(250, 25)
        # self.ui.appNameLabel.setPixmap(pixmap)

    def check(self):
        """
        检查用户输入的用户名和密码是否正确
        :return:
        """
        # 从数据库中取出所有用户信息, 将密码解密为明文后, 将用户名与密码明文拼接成 userInfo 以待后续比对
        c = self.conn.cursor()  # 创建数据库游标
        c.execute('SELECT * FROM userInfo')  # 执行查询语句
        rows = c.fetchall()  # 获取查询结果
        userInfo = ''
        for row in rows:
            userID, userCode = row
            userInfo = userInfo + userID + '\n' + func_decrypt_config(key, userCode) + '\n'
        # print('Get userInfo:' + userInfo)

        # 获取用户输入的用户名与密码
        userInput_Name = self.ui.userNameEdit.text()
        userInput_Password = self.ui.passwordEdit.text()

        # 调用 check_credentials 方法进行比对, 根据返回值(1: 匹配成功 2: 密码错误 3: 账号错误 0: 未知错误)进行相应提示与操作
        if self.check_credentials(userInfo, userInput_Name, userInput_Password) == 1:
            print('登录成功!')
            MessageBox(text='登陆成功!', mode=2, auto=True, time=2000, iconpath=':/home/icon/good-two.png').exec_()
            # 释放数据库资源
            self.conn.close()
            self.accept()
        elif self.check_credentials(userInfo, userInput_Name, userInput_Password) == 2:
            print('密码错误!')
            self.ui.passwordEdit.clear()

            # 进行计数, 设置共有 3 次尝试机会, 如果 3 次都未成功, 拒绝登录
            self.tryLoginTimes -= 1
            MessageBox(text='密码错误!你还有{}次机会!'.format(self.tryLoginTimes), mode=0).exec_()
            if self.tryLoginTimes == 0:
                self.conn.close()
                self.reject()
        elif self.check_credentials(userInfo, userInput_Name, userInput_Password) == 3:
            print('账号错误!')
            self.ui.userNameEdit.clear()
            self.ui.passwordEdit.clear()
            self.ui.userNameEdit.setFocus()

            # 进行计数, 设置共有 3 次尝试机会, 如果 3 次都未成功, 拒绝登录
            self.tryLoginTimes -= 1
            MessageBox(text='账号错误!你还有{}次机会!'.format(self.tryLoginTimes), mode=0).exec_()
            if self.tryLoginTimes == 0:
                self.conn.close()
                self.reject()

    def check_credentials(self, userinfo, userinput_name, userinput_password):
        """
        检查用户输入的用户名和密码是否与数据库中的记录匹配
        :param userinfo: 用户信息字符串, 包含从数据库中获取的用户名和密码
        :param userinput_name: 用户输入的用户名
        :param userinput_password: 用户输入的密码
        :return: 匹配结果 (1: 匹配成功 2: 密码错误 3: 账号错误 0: 未知错误)
        """
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
    """
    控制器类, 用于管理用户注册和登录逻辑
    Attributes:
        dataBaseName: 数据库文件名
        conn: 数据库连接对象
    """
    def __init__(self):
        """
        控制器类的初始化方法
        连接到 myDB 数据库, 检查是否存在 userInfo 表, 如果不存在, 进行创建
        """
        self.dataBaseName = 'myDB.db'
        self.conn = sql.connect(self.dataBaseName, isolation_level=None, uri=True)
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS userInfo 
                    (userID TEXT PRIMARY KEY NOT NULL,
                    userCode TEXT NOT NULL)
        ''')
        self.conn.commit()

    def show_register(self):
        """
        显示注册对话框
        :return: 对话框执行结果
        """
        self.regisDialog = registerDialog()
        return self.regisDialog.exec_()

    def show_login(self):
        """
        显示登录对话框
        :return: 对话框执行结果
        """
        self.logDialog = loginDialog()
        return self.logDialog.exec_()

    def openLoginSurface(self):
        """
        打开登陆界面
        :return: 登陆是否成功的布尔值
        """
        # 连接数据库, 查询现有用户信息
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
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    appIcon = QIcon(':/home/icon/suficon.png')
    app.setWindowIcon(appIcon)
    controller = Controller()
    if controller.openLoginSurface():
        Mymainwindow = MainWindow()
        Mymainwindow.show()
    else:
        sys.exit(0)
    sys.exit(app.exec_())
