from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QTableWidget, QAbstractItemView, QHeaderView, QHBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from utils.PageWidget import PageWidget


class PageTable(QVBoxLayout):
    # PageSize = 10

    # pageWidget = PageWidget()
    # tableWidget = QTableWidget()

    def __init__(self, header, rowCount: int):
        super().__init__()
        print(" PageTable init ,rowCount:" + str(rowCount) + ",header size:" + str(len(header)))

        self.tableWidget = QTableWidget(rowCount, len(header))
        self.tableWidget.setWindowTitle("Title")
        self.tableWidget.setHorizontalHeaderLabels(header)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.verticalHeader().setHidden(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 让表格挤满占个父容器

        self.tableWidget.setStyleSheet("QHeaderView::section {"
                                       "color: black;font:bold 14px \"微软雅黑\";"
                                       "text-align:center;"
                                       "height:25px;"
                                       "background-color: #d1dff0;"
                                       " border:1px solid #8faac9;"
                                       "border-left:none;"
                                       "}")
        hLayout = QHBoxLayout()
        self.pageWidget = PageWidget()
        hLayout.addWidget(self.pageWidget)

        qss = ".QLabel[page=\"true\"] { padding: 1px; }" + \
              ".QLabel[currentPage=\"true\"] { color: rgb(190, 0, 0);}" + \
              ".QLabel[page=\"true\"]:hover { color: white; border-radius: 4px; background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(53, 121, 238, 255), stop:1 rgba(0, 202, 237, 255));}"
        self.pageWidget.setStyleSheet(qss)

        self.addWidget(self.tableWidget)
        self.addLayout(hLayout)

        self.tableWidget.horizontalHeader().size()

    def SetData(self, DataList):
        for i in range(len(DataList)):
            Item = DataList[i]
            for j in range(len(Item) - 1):
                qItem = QTableWidgetItem(str(Item[j]))
                qItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                self.tableWidget.setItem(i, j, qItem)
            self.tableWidget.setCellWidget(i, len(Item) - 1, Item[-1])
