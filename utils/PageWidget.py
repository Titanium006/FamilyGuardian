
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QKeyEvent
from myDesign_win.PageWidget_ui import Ui_PageWidget


class PageWidget(QWidget):
    send_curPage = pyqtSignal(int)

    ui = Ui_PageWidget()
    blockSize = 0
    maxPage = 0
    pageLabels = []
    currentPage = 0

    def __init__(self, blockSize=3, parent=None):
        super().__init__(parent)
        self.ui.setupUi(self)
        self.setBlockSize(blockSize)
        self.ui.pageLineEdit.installEventFilter(self)
        self.ui.pageLineEdit.setValidator(QIntValidator(1, 10000000))

        self.ui.nextPageLabel.setProperty("page", "true")
        self.ui.previousPageLabel.setProperty("page", "true")
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
            label.setProperty("page", "true")
            label.installEventFilter(self)

            self.pageLabels.append(label)

            # 在这里把左边 3 个， 中间 3 个和右边 3 个都放到了页面上
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

    # def eventFilter(self, watched: 'QObject', e: 'QEvent') -> bool:
    def eventFilter(self, watched, e) -> bool:
        if e.type() == QEvent.MouseButtonRelease:
            page = -1
            if watched == self.ui.previousPageLabel:
                page = self.currentPage - 1
            if watched == self.ui.nextPageLabel:
                page = self.currentPage + 1
            for i in range(len(self.pageLabels)):
                if watched == self.pageLabels[i]:
                    # 在这里设置 "跳转到哪一页", 因为是 "读取当前标签的文字转化为数字", 所以不会受到我设置不同页码标签的影响
                    page = int(self.pageLabels[i].text())

            if page != -1:
                self.setCurrentPage(page, True)
                return True

        if watched == self.ui.pageLineEdit and e.type() == QEvent.KeyRelease:
            ke = e  # QKeyEvent
            if ke.key() == Qt.Key_Return or ke.key() == Qt.Key_Enter:
                # 在这里设置 "跳转到哪一页", 因为是 "读取当前标签的文字转化为数字", 所以不会受到我设置不同页码标签的影响
                self.setCurrentPage(int(self.ui.pageLineEdit.text()), True)
                return True

        return super().eventFilter(watched, e)

    def updatePageLabels(self):
        self.ui.leftSeparateLabel.hide()
        self.ui.rightSeparateLabel.hide()

        if self.maxPage <= self.blockSize * 3:
            for i in range(len(self.pageLabels)):
                if i < self.maxPage:
                    self.pageLabels[i].setText(str(i + 1))
                    self.pageLabels[i].show()
                else:
                    self.pageLabels[i].hide()

                if self.currentPage - 1 == i:
                    self.pageLabels[i].setProperty("currentPage", "true")
                else:
                    self.pageLabels[i].setProperty("currentPage", "false")

                self.pageLabels[i].setStyleSheet("/**/")
            return

        print("Bigger")
        c = self.currentPage
        n = self.blockSize
        m = self.maxPage
        # print('currentPage:' + str(c) + '\tblockSize:' + str(n) + '\tmaxPage:' + str(m))
        centerStartPage = 0     # int类型, 需要进行截断处理

        # 我觉得这里触发条件是没错的, 就是要改一下设置的页码而已
        if 1 <= c <= int(n + n / 2 + 1):

            print('1 <= {} <= {}'.format(c, int(n + n / 2 + 1)))

            centerStartPage = int(n + 1)
            self.ui.rightSeparateLabel.show()
        elif int(m - n - n / 2) <= c <= m:

            print('{} <= {} <= {}'.format(int(m - n - n / 2), c, m))

            centerStartPage = int(m - n - n + 1)
            self.ui.leftSeparateLabel.show()
        else:

            print('{} <= {} <= {}'.format(int(n + n / 2 + 1 + 1), c, int(m - n - n / 2 - 1)))

            centerStartPage = int(c - n / 2)
            self.ui.rightSeparateLabel.show()
            self.ui.leftSeparateLabel.show()

        # 在这里设置底下页码的标签
        for i in range(n):
            print('pageLabels {} {} {}'.format(i + 1, n + i + 1, 3 * n - i - 1 + 1))
            print('pageStr    {} {} {}'.format(i + 1, centerStartPage + i, m - i))
            self.pageLabels[i].setText(str(i + 1))
            # self.pageLabels[n + i].setText(str(centerStartPage + i + 1))          # 这个中间控件的效果达到了, 但是右边的控件会乱
            self.pageLabels[n + i].setText(str(centerStartPage + i))
            self.pageLabels[3 * n - i - 1].setText(str(m - i))

        for i in range(len(self.pageLabels)):
            page = int(self.pageLabels[i].text())
            # print('page: ' + str(page))
            if page == self.currentPage:
                self.pageLabels[i].setProperty("currentPage", "true")
            else:
                self.pageLabels[i].setProperty("currentPage", "false")

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
                self.send_curPage.emit(page)

    def setMaxPage(self, page: int):
        page = max(page, 1)
        if self.maxPage != page:
            self.maxPage = page
            self.currentPage = 1
            self.updatePageLabels()

    def setBlockSize(self, bSize: int):
        bSize = max(bSize, 3)
        if bSize % 2 == 0:
            bSize += 1
        self.blockSize = bSize
