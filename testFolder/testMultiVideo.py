######################################################
# PyCamera.py                                        #
# Copyright (c) 2021 By LiuHui. All Rights Reserved. #
#                                                    #
# Email: specterlh@163.com                           #
######################################################

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QCoreApplication, QThread, QObject, pyqtSignal
import cv2
import sys
import math
import numpy as np
import time
import os

'''PyQt5窗口页面'''


class Ui_MainWindow(QtWidgets.QWidget):
    '''窗口初始化'''

    def __init__(self, MainWindow):
        super().__init__(MainWindow)
        self.MainWindow = MainWindow  # 定义窗口控件
        self.threads = []  # 定义多线程数组
        self.caps = []  # 定义摄像头数组
        self.labels = []  # 定义摄像头显示位置
        self.timers = []  # 定义定时器， 用于控制显示帧率
        self.setupUi()  # 定义窗口页面布局

    '''设置页面布局'''

    def setupUi(self):
        self.MainWindow.setObjectName("MainWindow")  # 窗口控件名称
        self.MainWindow.resize(800, 600)  # 窗口控件尺寸

        self.centralwidget = QtWidgets.QWidget(self.MainWindow)  # 设置底层控件
        self.centralwidget.setObjectName("centralwidget")  # 设置底层控件名称

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)  # 设置网格布局控件
        self.gridLayout.setObjectName("gridLayout")  # 设置网格控件名称

        self.MainWindow.setCentralWidget(self.centralwidget)  # 绑定窗口底层控件

        self.statusbar = QtWidgets.QStatusBar(self.MainWindow)  # 添加状态栏
        self.statusbar.setObjectName("statusbar")
        self.MainWindow.setStatusBar(self.statusbar)

        self.action = QtWidgets.QAction(self.MainWindow)  # 添加菜单动作
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction(self.MainWindow)  # 添加菜单动作
        self.action_2.setObjectName("action_2")

        self.menubar = QtWidgets.QMenuBar(self.MainWindow)  # 添加菜单栏
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName("menubar")

        self.menu = QtWidgets.QMenu(self.menubar)  # 添加菜单事件
        self.menu.setObjectName("menu")
        self.menu.addAction(self.action)
        self.menu.addAction(self.action_2)

        self.menubar.addAction(self.menu.menuAction())  # 菜单栏添加事件
        self.MainWindow.setMenuBar(self.menubar)
        self.retranslateUi()  # 设置控件文本
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    '''设置控件显示文本'''

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "智慧视频"))
        self.menu.setTitle(_translate("MainWindow", "设置"))

        self.action.setText(_translate("MainWindow", "摄像头"))
        self.action.triggered.connect(self.refreshCamera)

        self.action_2.setText(_translate("MainWindow", "关闭"))
        self.action_2.triggered.connect(self.close_Window)

    '''扫码已有摄像头，返回编号'''

    def GetUsbCameraIO(self):
        ids = []
        for i in range(10):
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                ids.append(i)
        return ids

    '''关闭窗口'''

    def close_Window(self):
        for thread in self.threads:
            thread.quit()
        self.MainWindow.close()

    '''刷新摄像头布局'''

    def refreshCamera(self):
        # 停止现有的多线程
        for thread in self.threads:
            thread.quit()
        self.ids = self.GetUsbCameraIO()  # 获取当前所有可连接摄像头的id

        ids = np.array(self.ids)  # 将数组转换为矩阵
        n = len(ids)  # 获取矩阵长度
        cols = math.ceil(math.sqrt(n))  # 取矩阵开方下的最接近整数，向下取整
        rows = math.floor(math.sqrt(n))  # 取矩阵开方下的最接近整数，向上取整
        if cols * rows < n:  # 如果数量不够，增加一行
            rows = rows + 1
        arr = np.empty(cols * rows)  # 创建一个空矩阵
        arr[:n] = ids  # 空矩阵的前面为id矩阵
        arr[n:] = -1  # 空矩阵后面为-1
        arr = arr.reshape((rows, cols))  # 将矩阵转换为rows*cols的矩阵
        self.arr = arr
        # 循环创建布局及控件
        for i in range(rows):
            for j in range(cols):
                label = QtWidgets.QLabel(self.centralwidget)  # 创建label控件
                self.gridLayout.addWidget(label, i, j, 1, 1)  # 设置label布局
                thread_i = QThread()  # 创建多个线程
                timer = QtCore.QTimer()  # 创建定时器
                cap = myCamera(label, int(arr[i][j]), timer)  # 定义一个新的摄像机
                cap.signal.connect(self.flush)  # 摄像机可以触发状态改变
                cap.moveToThread(thread_i)  # 将摄像机绑定到线程
                timer.moveToThread(thread_i)  # 将定时器绑定到线程
                thread_i.started.connect(cap.started)  # 绑定线程起始事件
                thread_i.finished.connect(cap.finished)  # 绑定线程终止事件
                thread_i.start()  # 线程启动
                self.threads.append(thread_i)  # 记录线程
                self.caps.append(cap)  # 记录摄像机
                self.labels.append(label)  # 记录文本控件
                self.timers.append(timer)  # 记录计时器

    '''设置摄像头文本显示'''

    def flush(self, label, txt):
        label.setText(txt)


'''定义摄像机类'''


class myCamera(QObject):
    signal = pyqtSignal(QtWidgets.QLabel, str)  # 摄像机类返回信号

    '''初始化摄像机'''

    def __init__(self, label, capIndex, timer):
        super(myCamera, self).__init__()
        self.label = label
        self.timer_camera = timer  # 帧数定时器
        self.capIndex = capIndex  # 相机编号

    '''设置显示图片'''

    def show(self):
        pos = self.label.geometry()  # 获取label大小
        flag, image = self.cap.read()  # 读取摄像机图片
        # 图像上写入当前时间
        timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 获取当前时间，格式yyyy-mm-dd HH:MM:ss
        timestr = timestr + " Camera" + str(self.capIndex)
        cv2.putText(image, timestr, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        '''显示图片'''
        show = cv2.resize(image, (pos.width(), pos.height()))  # 调整摄像机图片尺寸
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 转换颜色到rgb
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[1] * 3,
                                 QtGui.QImage.Format_RGB888)  # 转换图片格式
        showImage = QtGui.QPixmap.fromImage(showImage)  # 转换图片格式
        self.label.setPixmap(showImage)  # 设置图片显示

    '''摄像头启动事件'''

    def started(self):
        self.timer_camera.timeout.connect(self.show)  # 设置计时器绑定
        self.signal.emit(self.label, "摄像头连接中，请稍候")  # 设置文本显示
        self.cap = cv2.VideoCapture(self.capIndex)
        print("start:Camera" + str(self.capIndex))
        self.timer_camera.start(30)

    '''摄像头停止事件'''

    def finished(self):
        self.timer_camera.stop()  # 关闭定时器
        self.cap.release()  # 释放视频流
        self.label.setText("摄像头已断开")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow(mainWindow)
    ui.setupUi()
    mainWindow.show()
    sys.exit(app.exec_())