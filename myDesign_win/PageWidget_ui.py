# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PageWidget_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PageWidget(object):
    def setupUi(self, PageWidget):
        PageWidget.setObjectName("PageWidget")
        PageWidget.resize(309, 23)
        PageWidget.setMaximumSize(QtCore.QSize(309, 16777215))
        PageWidget.setStyleSheet("")
        self.horizontalLayout = QtWidgets.QHBoxLayout(PageWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.previousPageLabel = QtWidgets.QLabel(PageWidget)
        self.previousPageLabel.setObjectName("previousPageLabel")
        self.horizontalLayout.addWidget(self.previousPageLabel)
        self.leftPagesWidget = QtWidgets.QWidget(PageWidget)
        self.leftPagesWidget.setObjectName("leftPagesWidget")
        self.horizontalLayout.addWidget(self.leftPagesWidget)
        self.leftSeparateLabel = QtWidgets.QLabel(PageWidget)
        self.leftSeparateLabel.setObjectName("leftSeparateLabel")
        self.horizontalLayout.addWidget(self.leftSeparateLabel)
        self.centerPagesWidget = QtWidgets.QWidget(PageWidget)
        self.centerPagesWidget.setObjectName("centerPagesWidget")
        self.horizontalLayout.addWidget(self.centerPagesWidget)
        self.rightSeparateLabel = QtWidgets.QLabel(PageWidget)
        self.rightSeparateLabel.setObjectName("rightSeparateLabel")
        self.horizontalLayout.addWidget(self.rightSeparateLabel)
        self.rightPagesWidget = QtWidgets.QWidget(PageWidget)
        self.rightPagesWidget.setObjectName("rightPagesWidget")
        self.leftSeparateLabel.raise_()
        self.horizontalLayout.addWidget(self.rightPagesWidget)
        self.nextPageLabel = QtWidgets.QLabel(PageWidget)
        self.nextPageLabel.setObjectName("nextPageLabel")
        self.horizontalLayout.addWidget(self.nextPageLabel)
        self.label = QtWidgets.QLabel(PageWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.pageLineEdit = QtWidgets.QLineEdit(PageWidget)
        self.pageLineEdit.setMinimumSize(QtCore.QSize(50, 0))
        self.pageLineEdit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pageLineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.pageLineEdit.setObjectName("pageLineEdit")
        self.horizontalLayout.addWidget(self.pageLineEdit)
        self.label_2 = QtWidgets.QLabel(PageWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        spacerItem1 = QtWidgets.QSpacerItem(45, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)

        self.retranslateUi(PageWidget)
        QtCore.QMetaObject.connectSlotsByName(PageWidget)

    def retranslateUi(self, PageWidget):
        _translate = QtCore.QCoreApplication.translate
        PageWidget.setWindowTitle(_translate("PageWidget", "Form"))
        self.previousPageLabel.setToolTip(_translate("PageWidget", "上一页"))
        self.previousPageLabel.setText(_translate("PageWidget", "<<"))
        self.leftSeparateLabel.setToolTip(_translate("PageWidget", "下一页"))
        self.leftSeparateLabel.setText(_translate("PageWidget", ".."))
        self.rightSeparateLabel.setToolTip(_translate("PageWidget", "下一页"))
        self.rightSeparateLabel.setText(_translate("PageWidget", ".."))
        self.nextPageLabel.setToolTip(_translate("PageWidget", "下一页"))
        self.nextPageLabel.setText(_translate("PageWidget", ">>"))
        self.label.setText(_translate("PageWidget", "第"))
        self.label_2.setText(_translate("PageWidget", "页"))