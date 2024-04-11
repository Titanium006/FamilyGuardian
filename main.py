import sys
import os
import re
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
from myDesign_win.home import Ui_MainWindow

QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)


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

    def gotoBlock(self, index: int):
        self.ui.stackedWidget.setCurrentIndex(index)

    def maxOrRestore(self):
        if not self.isMaxi:
            self.showMaximized()
            self.isMaxi = True
        else:
            self.showNormal()
            self.isMaxi = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
