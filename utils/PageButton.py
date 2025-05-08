from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton


# 自定义按钮类 PageButton, 继承自QPushButton
class PageButton(QPushButton):
    # 定义一个信号, 当按钮被点击时会发送包含按钮信息的列表
    send_myNo = pyqtSignal(list)

    def __init__(self, parent=None):
        """
        初始化PageButton类的实例
        :param parent:父级控件, 默认为None
        """
        super().__init__(parent)
        self.fileName = ''      # 文件名
        self.startTime = ''     # 录像开始时间
        self.endTime = ''       # 录像结束时间
        self.camNo = ''         # 摄像头编号
        self.btnNo = 0          # 按钮编号, 设定会从1开始

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        处理鼠标按下的事件, 当按钮被按下时发送包含按钮信息的信号
        :param event: 鼠标事件对象
        :return:
        """
        # 创建一个包含按钮相关信息的列表
        infoGroup = [self.startTime, self.endTime, self.camNo, self.fileName, self.btnNo]
        # 发送信号
        self.send_myNo.emit(infoGroup)
        # 调用父类的鼠标按下事件处理方法
        super().mousePressEvent(event)


# 自定义按钮类 UserDelButton, 继承自 QPushButton
class UserDelButton(QPushButton):
    # 定义一个信号, 当按钮被点击时会发送包含按钮信息的列表
    send_myNo = pyqtSignal(list)

    def __init__(self, parent=None):
        """
        初始化UserDelButton类的实例
        :param parent: 父级控件, 默认为None
        """
        super().__init__(parent)
        self.userID = ''    # 用户ID
        self.btnNo = 0      # 按钮编号, 设定会从1开始

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        处理鼠标按下事件, 当按钮被按下时发送包含用户信息的信号
        :param event: 鼠标事件对象
        :return:
        """
        # 创建一个包含用户相关信息的列表
        infoGroup = [self.userID, self.btnNo]
        # 发送信号
        self.send_myNo.emit(infoGroup)
        # 调用父类的鼠标按下事件处理方法
        super().mousePressEvent(event)
