# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'home.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(946, 679)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 0, 931, 681))
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox_4)
        self.groupBox_3.setStyleSheet("background-color: rgb(255, 170, 255);")
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.miniButton = QtWidgets.QPushButton(self.groupBox_3)
        self.miniButton.setObjectName("miniButton")
        self.horizontalLayout_2.addWidget(self.miniButton)
        self.maxiButton = QtWidgets.QPushButton(self.groupBox_3)
        self.maxiButton.setObjectName("maxiButton")
        self.horizontalLayout_2.addWidget(self.maxiButton)
        self.closeButton = QtWidgets.QPushButton(self.groupBox_3)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout_2.addWidget(self.closeButton)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.groupBox = QtWidgets.QGroupBox(self.groupBox_4)
        self.groupBox.setStyleSheet("background-color: rgb(184, 184, 184);")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setStyleSheet("background-color: rgb(255, 170, 127);")
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.page1Button = QtWidgets.QPushButton(self.groupBox_2)
        self.page1Button.setObjectName("page1Button")
        self.verticalLayout.addWidget(self.page1Button)
        self.page2Button = QtWidgets.QPushButton(self.groupBox_2)
        self.page2Button.setObjectName("page2Button")
        self.verticalLayout.addWidget(self.page2Button)
        self.page3Button = QtWidgets.QPushButton(self.groupBox_2)
        self.page3Button.setObjectName("page3Button")
        self.verticalLayout.addWidget(self.page3Button)
        self.page4Button = QtWidgets.QPushButton(self.groupBox_2)
        self.page4Button.setObjectName("page4Button")
        self.verticalLayout.addWidget(self.page4Button)
        self.page5Button = QtWidgets.QPushButton(self.groupBox_2)
        self.page5Button.setObjectName("page5Button")
        self.verticalLayout.addWidget(self.page5Button)
        spacerItem1 = QtWidgets.QSpacerItem(20, 180, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.stackedWidget = QtWidgets.QStackedWidget(self.groupBox)
        self.stackedWidget.setStyleSheet("background-color: rgb(170, 170, 255);")
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.out_video = QtWidgets.QLabel(self.page)
        self.out_video.setGeometry(QtCore.QRect(0, 0, 791, 591))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.out_video.sizePolicy().hasHeightForWidth())
        self.out_video.setSizePolicy(sizePolicy)
        self.out_video.setStyleSheet("background-color: rgb(0, 170, 255);")
        self.out_video.setText("")
        self.out_video.setObjectName("out_video")
        self.curTimeLabel = QtWidgets.QLabel(self.page)
        self.curTimeLabel.setGeometry(QtCore.QRect(620, 0, 171, 51))
        self.curTimeLabel.setStyleSheet("background-color: rgba(0, 0, 0, 150);\n"
"font: 11pt \"Arvo\";\n"
"color: white;")
        self.curTimeLabel.setText("")
        self.curTimeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.curTimeLabel.setObjectName("curTimeLabel")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.tableWidget = QtWidgets.QTableWidget(self.page_2)
        self.tableWidget.setGeometry(QtCore.QRect(10, 20, 771, 511))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(15)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(12, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(13, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(14, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.label_5 = QtWidgets.QLabel(self.page_3)
        self.label_5.setGeometry(QtCore.QRect(270, 250, 221, 121))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.label_6 = QtWidgets.QLabel(self.page_4)
        self.label_6.setGeometry(QtCore.QRect(280, 230, 221, 121))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.stackedWidget.addWidget(self.page_4)
        self.page_5 = QtWidgets.QWidget()
        self.page_5.setObjectName("page_5")
        self.label_7 = QtWidgets.QLabel(self.page_5)
        self.label_7.setGeometry(QtCore.QRect(260, 240, 221, 121))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.stackedWidget.addWidget(self.page_5)
        self.horizontalLayout.addWidget(self.stackedWidget)
        self.verticalLayout_2.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "Label"))
        self.label.setText(_translate("MainWindow", "FamilyGuard"))
        self.miniButton.setText(_translate("MainWindow", "-"))
        self.maxiButton.setText(_translate("MainWindow", "O"))
        self.closeButton.setText(_translate("MainWindow", "×"))
        self.page1Button.setText(_translate("MainWindow", "Page1"))
        self.page2Button.setText(_translate("MainWindow", "Page2"))
        self.page3Button.setText(_translate("MainWindow", "Page3"))
        self.page4Button.setText(_translate("MainWindow", "Page4"))
        self.page5Button.setText(_translate("MainWindow", "Page5"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.tableWidget.verticalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.tableWidget.verticalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.tableWidget.verticalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.tableWidget.verticalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.tableWidget.verticalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.tableWidget.verticalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        item = self.tableWidget.verticalHeaderItem(10)
        item.setText(_translate("MainWindow", "11"))
        item = self.tableWidget.verticalHeaderItem(11)
        item.setText(_translate("MainWindow", "12"))
        item = self.tableWidget.verticalHeaderItem(12)
        item.setText(_translate("MainWindow", "13"))
        item = self.tableWidget.verticalHeaderItem(13)
        item.setText(_translate("MainWindow", "14"))
        item = self.tableWidget.verticalHeaderItem(14)
        item.setText(_translate("MainWindow", "15"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "序号"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "报警类型"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "触发事件(持续时间)"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "查看回放"))
        self.label_5.setText(_translate("MainWindow", "This is Page 3"))
        self.label_6.setText(_translate("MainWindow", "This is Page 4"))
        self.label_7.setText(_translate("MainWindow", "This is Page 5"))