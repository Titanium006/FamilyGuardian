import sys
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QPixmap, QIcon
import apprcc_rc


# 单按钮对话框，出现到指定时长后自动消失
class MessageBox(QMessageBox):
    def __init__(self, *args,
                 title='FAMILYGUARD',
                 count=0,
                 time=1000,
                 auto=False,
                 mode=0,  # 这里用mode来设置展示什么按钮(0:Only Close 1:Yes & No 2:None(配合定时关闭))
                 iconpath=':/home/icon/caution.png',
                 **kwargs):
        super(MessageBox, self).__init__(*args, **kwargs)
        self._count = count
        self._time = time
        self._auto = auto  # 是否自动关闭
        # assert count > 0  # 必须大于0
        assert time >= 500  # 必须>=500毫秒
        self.setStyleSheet('''
                            QDialog{background:rgb(75, 75, 75);
                                    color:white;}
                            QLabel{ background: rgb(75, 75, 75);
                                    font: 13pt "等线";
                                    color:white;
                                    padding-left: -4px;
                                    margin-top: 15px;}''')
        self.setWindowTitle(title)
        pixmap = QPixmap(iconpath)
        pixmap = pixmap.scaled(50, 50)
        self.setIconPixmap(pixmap)

        # self.setStandardButtons(self.Close)  # 关闭按钮
        self.addButton(self.Close)
        self.closeBtn = self.button(self.Close)  # 获取关闭按钮
        self.closeBtn.clicked.connect(self.accept)
        if count > 0 or auto:
            self.closeBtn.setText('关闭(%s)' % self._count)
            self.closeBtn.setEnabled(False)
            self._timer = QTimer(self, timeout=self.doCountDown)
            self._timer.start(self._time)
        else:
            self.closeBtn.setText('关闭')
        if mode == 1:
            self.closeBtn.setVisible(False)
            self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        elif mode == 2:
            self.closeBtn.setVisible(False)

    def doCountDown(self):
        self.closeBtn.setText('关闭(%s)' % self._count)
        self._count -= 1
        if self._count <= -1:
            self.closeBtn.setText('关闭')
            self.closeBtn.setEnabled(True)
            self._timer.stop()
            if self._auto:  # 自动关闭
                self.accept()
                # self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # a0.ignore()       如果使用.ignore(), 点击×按钮就不会关闭窗口
        #                   (关闭按钮的行为是由窗口系统管理的，而不是由 QMessageBox 本身控制)
        #                   所以无法直接设置右上角×按钮不可用, 所以可以采用.ignore()的方式变相实现
        a0.accept()
        self.reject()


# 如果想出现过一段时间再允许用户关闭的按钮, 可以设置count秒数, 然后time=1000, auto为False就行, 例:
#     msgBox = MessageBox(count=5, time=1000, text='回放文件不存在或已被清理!', auto=False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    msgBox = MessageBox(title='FAMILYGUARD', text='回放文件不存在或已被清理!', mode=0)
    response = msgBox.exec_()
    if (response == QMessageBox.Rejected or response == QMessageBox.Accepted
            or response == QMessageBox.No or response == QMessageBox.Yes):
        sys.exit(0)
    sys.exit(app.exec_())
