from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIntValidator, QKeyEvent
from myDesign_win.PageWidget_ui import Ui_PageWidget

class PageWidget(QWidget):
    ui = Ui_PageWidget()
    blockSize = 0
    maxPage = 0
    pageLabels = []
    currentPage = 0

    def __init__(self, blockSize = 3, parent=None):
        super().__init__(parent)
        self.setBlockSize(blockSize)
        self.ui.pageLineEdit.installEventFilter(self)
        self.ui.pageLineEdit.setValidator(QIntValidator(1, 10000000))

        self.ui.nextPageLabel.setProperty("page", "True")
        self.ui.previousPageLabel.setProperty("page", "True")
        self.ui.nextPageLabel.installEventFilter(self)
        self.ui.previousPageLabel.installEventFilter(self)

        leftLayout = QHBoxLayout()
        centerLayout = QHBoxLayout()
        rightLayout = QHBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.setSpacing(0)
        centerLayout.setContentsMargins(0, 0, 0, 0)
        centerLayout.setSpacing(0)
        rightLayout.setContentsMargins(0, 0, 0, 0)
        rightLayout.setSpacing(0)

        for i in range(self.blockSize * 3):
            label = QLabel(str(i + 1))
            label.setProperty("page", "True")
            label.installEventFilter(self)

            self.pageLabels.append(label)

            if i < self.blockSize:
                leftLayout.addWidget(label)
            elif i < self.blockSize * 2:
                centerLayout.addWidget(label)
            else:
                rightLayout.addWidget(label)

        self.ui.leftPagesWidget.setLayout(leftLayout)
        self.ui.centerPagesWidget.setLayout(centerLayout)
        self.ui.rightPagesWidget.setLayout(rightLayout)

        self.setMaxPage(1)

    def eventFilter(self, watched: 'QObject', e: 'QEvent') -> bool:
        if e.type() == QEvent.MouseButtonRelease:
            page = -1
            if watched == self.ui.previousPageLabel:
                page = self.currentPage - 1
            if watched == self.ui.nextPageLabel:
                page = self.currentPage + 1
            for i in range(self.pageLabels.count()):
                if watched == self.pageLabels[i]:
                    page = int(self.pageLabels[i].text())       #####

            if page != -1:
                self.setCurrentPage(page, True)
                return True

        if watched == self.ui.pageLineEdit and e.type() == QEvent.KeyRelease:
            ke = e              # QKeyEvent
            if ke.key() == Qt.Key_Return or ke.key() == Qt.Key_Enter:
                self.setCurrentPage(int(self.ui.pageLineEdit.text()), True)
                return True

        return super().eventFilter(watched, e)

    def updatePageLabels(self):
        self.ui.leftSeparateLabel.hide()
        self.ui.rightPagesWidget.hide()

        if self.maxPage <= self.blockSize * 3:
            for i in range(self.pageLabels.count()):
                if i < self.maxPage:
                    self.pageLabels[i].setText(str(i + 1))
                    self.pageLabels[i].show()
                else:
                    self.pageLabels[i].hide()

                if self.currentPage - 1 == i:
                    self.pageLabels[i].setProperty("currentPage", "True")
                else:
                    self.pageLabels[i].setProperty("currentPage", "False")

                self.pageLabels[i].setStyleSheet("/**/")

        c = self.currentPage
        n = self.blockSize
        m = self.maxPage
        centerStartPage = 0
        if 1 <= c <= n + n / 2 + 1:
            centerStartPage = n + 1
            self.ui.rightSeparateLabel.show()
        elif m - n - n / 2 <= c <= m:
            centerStartPage = m - n - n + 1
            self.ui.leftSeparateLabel.show()
        else:
            centerStartPage = c - n / 2
            self.ui.rightSeparateLabel.show()
            self.ui.leftSeparateLabel.show()

        for i in range(n):
            self.pageLabels[i].setText(str(i + 1))
            self.pageLabels[n + i].setText(str(centerStartPage + i))
            self.pageLabels[3 * n - i - 1].setText(str(m - i))

        for i in range(self.pageLabels.count()):
            page = int(self.pageLabels[i].text())
            if page == self.currentPage:
                self.pageLabels[i].setProperty("currentPage", "True")
            else:
                self.pageLabels[i].setProperty("currentPage", "False")

            self.pageLabels[i].setStyleSheet("/**/")
            self.pageLabels[i].show()

    def setCurrentPage(self, page: int, signalEmitted: bool):
        page = max(page, 1)
        page = min(page, self.maxPage)

        if page != self.currentPage:
            self.currentPage = page
            self.updatePageLabels()
            if signalEmitted:
                # emit currentPageChanged(page);
                pass

    def setMaxPage(self, page: int):
        page = max(page, 1)
        if self.maxPage != page:
            self.maxPage = page
            self.currentPage = 1
            self.updatePageLabels()

    def setBlockSize(self, bSize: int):
        bSize = max(bSize, 3)
        if (bSize % 2 == 0):
            bSize += 1
        self.blockSize = bSize
