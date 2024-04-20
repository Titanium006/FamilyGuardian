# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
# from PyQt5.QtCore import QUrl
#
# # 创建应用程序对象
# app = QApplication([])
#
# # 创建媒体播放器对象
# player = QMediaPlayer()
#
# # 打开视频文件
# url = QUrl.fromLocalFile("E:/电影/环法纪录片/环法 逆风飞驰 - 2.E2 欢迎来到地狱(Av742064678,P2).mp4")
# content = QMediaContent(url)
# player.setMedia(content)
#
# # 设置要跳转到的位置（单位：毫秒）
# target_position = 30000  # 例如，跳转到第30秒
# player.setPosition(target_position)
#
# # 播放视频
# player.play()
#
# # 运行应用程序
# app.exec_()

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建媒体播放器对象
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # 创建视频显示窗口
        self.video_widget = QVideoWidget()

        # 设置媒体对象到播放器
        url = QUrl.fromLocalFile("E:/电影/环法纪录片/环法 逆风飞驰 - 2.E2 欢迎来到地狱(Av742064678,P2).mp4")
        content = QMediaContent(url)
        self.player.setMedia(content)

        # 设置视频显示窗口到播放器
        self.player.setVideoOutput(self.video_widget)

        # 设置要跳转到的位置（单位：毫秒）
        target_position = 30000  # 例如，跳转到第30秒
        self.player.setPosition(target_position)

        # 播放视频
        self.player.play()

        # 设置主窗口布局
        self.setCentralWidget(self.video_widget)

        # 调整窗口大小和标题
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Video Player")

        # 显示窗口
        self.show()


if __name__ == "__main__":
    app = QApplication([])
    window = VideoPlayer()
    app.exec_()

