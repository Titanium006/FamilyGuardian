from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton

class PageButton(QPushButton):
    send_myNo = pyqtSignal(list)
    startTime = ''
    endTime = ''
    camNo = ''
    btnNo = 0  # 设定会从1开始

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        print('Enter PageButton Press!')
        infoGroup = [self.startTime, self.endTime, self.camNo, self.btnNo]
        self.send_myNo.emit(infoGroup)
        super().mousePressEvent(event)
        # event.accept()
