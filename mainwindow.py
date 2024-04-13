import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTableWidget
from utils.PageWidget import PageWidget
from utils.PageTable import PageTable
from myDesign_win.mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    ui = Ui_MainWindow()
    Datalist = [[]]
    RowIndex = 0
    pageCount = 50
    # pageTable = PageTable()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
        # header = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]
        header = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
        self.pageTable = PageTable(header, 5)
        # self.pageTable = PageTable(header, 30)
        self.ui.testLayout.addLayout(self.pageTable)
        self.pageTable.pageWidget.send_curPage.connect(lambda x: self.PageChange(x))

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
