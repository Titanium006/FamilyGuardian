# from PyQt5.QtWidgets import QApplication, QTableView, QPushButton, QWidget, QVBoxLayout, QStyledItemDelegate
# from PyQt5.QtCore import Qt, QModelIndex
# from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
#
# class ButtonDelegate(QStyledItemDelegate):
#     def __init__(self, parent=None):
#         super(ButtonDelegate, self).__init__(parent)
#
#     def paint(self, painter, option, index):
#         if index.column() == 1:  # 在第二列中绘制按钮
#             button = QPushButton("Click me", self.parent())
#             button.setGeometry(option.rect)
#             button.clicked.connect(lambda: self.clicked(index))
#             button.show()
#         else:
#             super(ButtonDelegate, self).paint(painter, option, index)
#
#     def clicked(self, index):
#         print("Button clicked at row:", index.row())
#
# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.initUI()
#
#     def initUI(self):
#         self.setWindowTitle("QTableView with Button")
#         self.setGeometry(100, 100, 600, 400)
#
#         layout = QVBoxLayout(self)
#
#         tableview = QTableView(self)
#         layout.addWidget(tableview)
#
#         model = QStandardItemModel(4, 3)
#         tableview.setModel(model)
#
#         delegate = ButtonDelegate(self)
#         tableview.setItemDelegate(delegate)
#
#         self.populateModel(model)
#
#     def populateModel(self, model):
#         for row in range(model.rowCount()):
#             for col in range(model.columnCount()):
#                 item = QStandardItem("Row{} Col{}".format(row, col))
#                 model.setItem(row, col, item)
#
# if __name__ == '__main__':
#     import sys
#     from PyQt5.QtWidgets import QApplication, QStyledItemDelegate, QTableView
#     app = QApplication(sys.argv)
#     ex = Example()
#     ex.show()
#     sys.exit(app.exec_())

#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
在单元格中放置控件

setItem：将文本放到单元格中
setCellWidget：将控件放到单元格中
setStyleSheet：设置控件的样式（QSS）
"""
import sys
from PyQt5.QtWidgets import QWidget, QTableWidget, QHBoxLayout, QApplication, QTableWidgetItem, QAbstractItemView, QComboBox, QPushButton


class PlaceControlInCell(QWidget):
    def __init__(self):
        super(PlaceControlInCell, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("在单元格中放置控件")
        self.resize(430, 300)
        layout = QHBoxLayout()

        tablewidget = QTableWidget()
        tablewidget.setRowCount(4)
        tablewidget.setColumnCount(3)

        layout.addWidget(tablewidget)

        tablewidget.setHorizontalHeaderLabels(["姓名", "性别", "体重/kg"])
        textItem = QTableWidgetItem("小明")
        tablewidget.setItem(0, 0, textItem)

        # 在性别中添加下拉选项控件， 只能从下面两个中选择，不能自己输入
        combox = QComboBox()
        combox.addItem("男")
        combox.addItem("女")
        # QSS Qt StyleSheet， 相当于CSS, 给combox控件添加样式
        combox.setStyleSheet("QComboBox{margin:3px};")
        tablewidget.setCellWidget(0, 1, combox)

        modifyButton = QPushButton("修改")
        # 设置默认是按下的状态，选中状态
        modifyButton.setDown(True)
        modifyButton.setStyleSheet("QPushButton{margin:3px};")
        tablewidget.setCellWidget(0, 2, modifyButton)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = PlaceControlInCell()
    example.show()
    sys.exit(app.exec_())
