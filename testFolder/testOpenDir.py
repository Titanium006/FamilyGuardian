import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("选择的目录路径将显示在这里")
        layout.addWidget(self.label)

        # 创建按钮，点击后弹出选择目录对话框
        self.btn = QPushButton('选择目录', self)
        self.btn.clicked.connect(self.showDialog)
        layout.addWidget(self.btn)

        self.setLayout(layout)
        self.setWindowTitle('Select Directory Example')
        self.show()

    def showDialog(self):
        # 打开选择目录对话框
        directory = QFileDialog.getExistingDirectory(self, "选择目录", "/")
        if directory:
            self.label.setText("选择的目录路径为: " + directory)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
