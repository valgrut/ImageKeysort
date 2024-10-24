from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)


class VideoWidget(QWidget):

    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoURL = ""

        btnSize = QSize(16, 16)
        videoWidget = QVideoWidget()

        # openButton = QPushButton("Open Video")
        # openButton.setToolTip("Open Video File")
        # openButton.setStatusTip("Open Video File")
        # openButton.setFixedHeight(24)
        # openButton.setIconSize(btnSize)
        # openButton.setFont(QFont("Noto Sans", 8))
        # openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))
        # openButton.clicked.connect(self.abrir)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        # controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")

    def playVideo(self):
        self.play()

    def updateVideo(self, path):
        self.videoURL = path
        self.abrir()

    def abrir(self):
        # fileName, _ = QFileDialog.getOpenFileName(self, "Select Media",
        #         ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        fileName = self.videoURL

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(fileName)
            # self.play()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())



#
# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     player = VideoWidget()
#     player.setWindowTitle("Player")
#     player.resize(900, 600)
#     player.show()
#     sys.exit(app.exec())


#
# from PyQt5.QtCore import Qt, QUrl
# from PyQt5.QtGui import QPixmap, QMovie
# from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
# from PyQt5.QtMultimediaWidgets import QVideoWidget
# from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
#
# from Styles import Styles
#
# class VideoWidget(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.setStyleSheet(f"""
#             width: 100px;
#             border: 1px solid black;
#             border-radius: {Styles.widgetBorderRadius}px;
#             padding: 3px;
#             background-color: rgb(100, 130, 189);
#         """)
#
#         # self.videoView = QMovie()
#         self.player = QMediaPlayer()
#         self._video_widget = QVideoWidget()
#         self.player.setVideoOutput(self._video_widget)
#
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(self._video_widget)
#         self.setLayout(self.layout)
#
#         # TODO: add video-controlling buttons
#
#     #
#     # def updateVideo(self, img_path):
#     #     self.pixmap.load(img_path)
#     #     self.pixmap = self.pixmap.scaled(900, 770, Qt.KeepAspectRatio)
#     #     self.label.setPixmap(self.pixmap)
#
#     def updateVideo(self, path):
#         self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
#
#     def playVideo(self):
#         self.player.play()
#
#     def stopVideo(self):
#         self.player.stop()
