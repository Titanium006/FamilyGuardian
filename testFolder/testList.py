import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ListWidget(QListWidget):
    def click(self,item):
        QMessageBox.information(self,'ListWidget','你选择了：'+item.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    listWidget = ListWidget()
    listWidget.setWindowTitle('QListWidget的使用')
    #添加条目
    listWidget.addItem('item1')
    listWidget.addItem('item2')
    listWidget.addItem('item3')
    listWidget.addItem('item4')
    #绑定信号发射事件
    listWidget.itemClicked.connect(listWidget.click)
    listWidget.show()
    sys.exit(app.exec_())

