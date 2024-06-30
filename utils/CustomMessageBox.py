# 导入必要的模块
import sys
import os
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import apprcc_rc


# 单按钮对话框，出现到指定时长后自动消失
# 自定义信息框类, 继承自QMessageBox
class MessageBox(QMessageBox):
    def __init__(self, *args,
                 title='FAMILYGUARD',   # 默认标题
                 count=0,               # 倒计时计数
                 time=1000,             # 倒计时间隔, 单位毫秒
                 auto=False,            # 是否自动关闭
                 mode=0,  # 这里用mode来设置展示什么按钮(0:Only Close 1:Yes & No 2:None(配合定时关闭) 3:Red Alarm)
                 iconpath=':/home/icon/caution.png',    # 图标路径
                 **kwargs):
        """
        初始化MessageBox类的实例
        :param args:
        :param title: 标题, 默认为 FAMILYGUARD
        :param count: 倒计时计数, 默认为 0
        :param time: 倒计时间隔, 单位毫秒, 默认为 1000
        :param auto: 是否自动关闭, 默认为 False
        :param mode: 设置MessageBox展示什么按钮, (0:Only Close 1:Yes & No 2:None(配合定时关闭) 3:Red Alarm)
        :param iconpath: 图标路径
        :param kwargs:
        """
        super(MessageBox, self).__init__(*args, **kwargs)

        # 初始化成员变量
        self._count = count
        self._time = time
        self._auto = auto  # 自动关闭标志

        # 获取当前目录和报警音频文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        media_dir = os.path.join(current_dir, 'media')
        file_path = os.path.join(media_dir, 'Alarm.mp3')
        file_path = os.path.abspath(file_path)

        # 初始化媒体播放器
        self.media_player = QMediaPlayer()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))

        # 连接按钮点击信号与停止音频的槽方法
        self.buttonClicked.connect(self.stop_audio)

        # assert count > 0  # 必须大于0
        assert time >= 500  # 确保倒计时时间必须>=500毫秒

        # 设置窗口标题和图标
        self.setWindowTitle(title)
        pixmap = QPixmap(iconpath)
        pixmap = pixmap.scaled(50, 50)
        self.setIconPixmap(pixmap)

        # 根据模式设置不同的样式表
        if mode == 3:
            self.setStyleSheet('''
                                QDialog{background: rgb(237, 45, 48);
                                        color:white;}
                                QLabel{ background: rgb(237, 45, 48);
                                        font: 13pt "等线";
                                        color:white;
                                        padding-left: -4px;
                                        margin-top: 15px;}''')
        else:
            self.setStyleSheet('''
                                QDialog{background:rgb(75, 75, 75);
                                        color:white;}
                                QLabel{ background: rgb(75, 75, 75);
                                        font: 13pt "等线";
                                        color:white;
                                        padding-left: -4px;
                                        margin-top: 15px;}''')

        # self.setStandardButtons(self.Close)  # 关闭按钮
        # 添加关闭按钮
        self.addButton(self.Close)
        self.closeBtn = self.button(self.Close)  # 获取关闭按钮
        self.closeBtn.clicked.connect(self.accept)

        # 如果倒计时大于 0 或者自动关闭标志为真, 设置倒计时功能
        if count > 0 or auto:
            self.closeBtn.setText('关闭(%s)' % self._count)
            self.closeBtn.setEnabled(False)
            self._timer = QTimer(self, timeout=self.doCountDown)
            self._timer.start(self._time)
        else:
            self.closeBtn.setText('关闭')

        # 根据模式设置按钮和音频播放
        if mode == 1:
            self.closeBtn.setVisible(False)
            self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        elif mode == 2:
            self.closeBtn.setVisible(False)
        elif mode == 3:
            self.media_player.play()

    def doCountDown(self):
        """
        处理倒计时
        :return:
        """
        self.closeBtn.setText('关闭(%s)' % self._count)
        self._count -= 1
        if self._count <= -1:
            self.closeBtn.setText('关闭')
            self.closeBtn.setEnabled(True)
            self._timer.stop()
            if self._auto:  # 自动关闭
                self.accept()
                # self.close()

    def stop_audio(self):
        """
        停止音频播放
        :return:
        """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        重写关闭时间处理方法
        :param a0: 关闭事件
        :return:
        """
        # a0.ignore()       如果使用.ignore(), 点击×按钮就不会关闭窗口
        #                   (关闭按钮的行为是由窗口系统管理的，而不是由 QMessageBox 本身控制)
        #                   所以无法直接设置右上角×按钮不可用, 所以可以采用.ignore()的方式变相实现
        a0.accept()         # 接受关闭事件
        self.reject()       # 关闭消息框


# 如果想出现过一段时间再允许用户关闭的按钮, 可以设置count秒数, 然后time=1000, auto为False就行, 例:
#     msgBox = MessageBox(count=5, time=1000, text='回放文件不存在或已被清理!', auto=False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    msgBox = MessageBox(title='FAMILYGUARD', text='回放文件不存在或已被清理!', mode=3)
    response = msgBox.exec_()
    if (response == QMessageBox.Rejected or response == QMessageBox.Accepted
            or response == QMessageBox.No or response == QMessageBox.Yes):
        sys.exit(0)
    sys.exit(app.exec_())
