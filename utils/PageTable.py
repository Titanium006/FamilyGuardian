import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QTableWidget, QAbstractItemView, QHeaderView
from PyQt5.QtWidgets import QTableWidgetItem, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from utils.PageWidget import PageWidget
import apprcc_rc


class PageTable(QVBoxLayout):
    # PageSize = 10

    # pageWidget = PageWidget()
    # tableWidget = QTableWidget()

    def __init__(self, header, rowCount: int):
        super().__init__()
        print(" PageTable init ,rowCount:" + str(rowCount) + ",header size:" + str(len(header)))
        self.rowCount = rowCount
        self.headerLen = len(header)
        self.tableWidget = QTableWidget(rowCount, len(header))
        self.tableWidget.setWindowTitle("Title")
        self.tableWidget.setHorizontalHeaderLabels(header)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.verticalHeader().setHidden(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 让表格挤满占个父容器
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setStyleSheet("QHeaderView::section {"
                                       "color: black;font:bold 14px \"DengXian\";"
                                       "text-align:center;"
                                       "height:45px;"
                                       "background-color: #d1dff0;"
                                       "border: none;"
                                       "border-left:none;"
                                       "border-bottom: 1px solid #8faac9;"
                                       "}"
                                       "QHeaderView::section:first {"
                                       "border-top-left-radius: 3px;"
                                       "}"
                                       "QHeaderView::section:last {"
                                       "border-top-right-radius: 3px;"
                                       "}"
                                       "QTableWidget {"
                                       "border-radius: 5px;"
                                       "border: 1px solid #8faac9;"
                                       # "background: rgb(255, 255, 255);"
                                       "alternate-background-color: rgb(251, 251, 251);"
                                       "outline: none;"
                                       "font:bold 13px \"DengXian\";"
                                       "}"
                                       "QTableWidget::Item {"
                                       "border: 0px;"
                                       "border-bottom: 1px solid #dcdcdc"
                                       "}"
                                       "QTableWidget::Item:hover {"
                                       "background-color: rgb(245, 245, 245);"
                                       "}"
                                       "QTableWidget::Item:Selected {"
                                       "background-color: rgb(242, 242, 242);"
                                       "color: rgb(0, 0, 0);"
                                       "}")
        hLayout = QHBoxLayout()
        self.pageWidget = PageWidget()
        hLayout.addWidget(self.pageWidget)

        qss = ".QLabel[page=\"true\"] { padding: 1px; font: bold 10pt \"DengXian\";}" + \
              (".QLabel[currentPage=\"true\"] { border-radius: 8px; border: 1px solid rgb(65, 93, 234); background-color: rgb(65, 93, 234);"
               "color: rgb(255, 255, 255);}") + \
              (".QLabel[page=\"true\"]:hover { color: white; border-radius: 8px; "
               "background-color: rgb(65, 93, 234);}") + \
              '''#pageLineEdit{background: transparent;border: none;border-bottom: 1px solid rgb(0, 0, 0);padding: -1px;font: 25 10pt "DengXian";}
                    #label{font: bold 11pt "DengXian";}#label_2{font: bold 11pt "DengXian";}
                    '''
        self.pageWidget.setStyleSheet(qss)
        # qlineargradient(spread:reflect, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(53, 121, 238, 255), stop:1 rgba(0, 202, 237, 255))

        self.addWidget(self.tableWidget)
        self.addLayout(hLayout)

        self.tableWidget.horizontalHeader().size()

    def SetData(self, DataList, dataType=1):
        iconPath = ''
        iconSize = 1
        if dataType == 0 or dataType == 1:
            iconPath = ':/home/icon/arrow-right.png'
            iconSize = 20
        elif dataType == 2:
            iconPath = ':/home/icon/people-delete.png'
            iconSize = 25
        if len(DataList) < self.rowCount:
            for i in range(0, len(DataList)):
                widget = self.tableWidget.cellWidget(i, self.headerLen - 1)
                if widget is not None:
                    widget.setIcon(QIcon(iconPath))
                    widget.setEnabled(True)
                    widget.setIconSize(QSize(iconSize, iconSize))
                    widget.setDown(False)
                    widget.show()
            for i in range(len(DataList), self.rowCount):
                for j in range(self.headerLen - 1):
                    if dataType == 0 and j == 3:
                        self.tableWidget.removeCellWidget(i, j)
                        continue
                    itm = QTableWidgetItem("")
                    itm.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                    self.tableWidget.setItem(i, j, itm)
                widget = self.tableWidget.cellWidget(i, self.headerLen - 1)
                if widget is not None:
                    widget.setIcon(QIcon())
                    widget.setEnabled(False)
                    widget.setDown(False)
                    widget.hide()
        else:
            for i in range(self.rowCount):
                widget = self.tableWidget.cellWidget(i, self.headerLen - 1)
                if widget is not None:
                    widget.setIcon(QIcon(iconPath))
                    widget.setEnabled(True)
                    widget.setIconSize(QSize(iconSize, iconSize))
                    widget.show()
        if len(DataList) == 0 or (DataList[0]) == 0:
            return
        for i in range(len(DataList)):
            Item = DataList[i]
            for j in range(len(Item) - 1):
                qItem = QTableWidgetItem(str(Item[j]))
                qItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                if dataType == 0 and j == 3:
                    qItem.setText('')
                    label = QLabel()
                    pixmap = QPixmap()
                    if str(Item[j]) == '0':  # 烟雾
                        pixmap = QPixmap(':/home/icon/fog.png')
                    elif str(Item[j]) == '1':  # 火焰
                        pixmap = QPixmap(':/home/icon/fire.png')
                    elif str(Item[j]) == '2':  # 陌生人员
                        pixmap = QPixmap(':/home/icon/people.png')
                    pixmap = pixmap.scaled(25, 25)
                    label.setPixmap(pixmap)
                    # label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                    # label.setMinimumHeight(30)
                    # label.setMinimumWidth(30)
                    label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                    label.setStyleSheet('QLabel {background: transparent;}')
                    self.tableWidget.setCellWidget(i, j, label)
                else:
                    self.tableWidget.setItem(i, j, qItem)
            self.tableWidget.setCellWidget(i, len(Item) - 1, Item[-1])
