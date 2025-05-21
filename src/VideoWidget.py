from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize, pyqtSlot, QSizeF
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsView, QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)

from src.Styles import Styles


# VideoViewWidget (Nic spolecneho s QVideoWidget)
class VideoWidget(QWidget):

    def __init__(self):
        super().__init__()

        # self.setStyleSheet(f"""
        #     width: 100px;
        #     border: 1px solid black;
        #     border-radius: {Styles.widgetBorderRadius}px;
        #     padding: 3px;
        #     background-color: rgb(100, 100, 189);
        # """)

        self.videoURL = ""

        self.defaultVolume = 50

        scene = QGraphicsScene()
        self.graphicsView = QGraphicsView(scene)
        self.videoItem = QGraphicsVideoItem()
        self.graphicsView.setStyleSheet("border: 2px solid black;")
        scene.addItem(self.videoItem)
        size = self.graphicsView.size()
        self.videoItem.setSize(QSizeF(size.width()-30, size.height()-30))

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.videoItem)
        
        layoutQVideoWidget = QVBoxLayout()
        layoutQVideoWidget.addWidget(self.graphicsView)
        
        btnSize = QSize(16, 16)

        self.playButton = QPushButton("Play")
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.togglePlayPause)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        # self.positionSlider.setTickInterval(3)
        # self.positionSlider.setTickPosition(QSlider.TicksLeft)
        self.positionSlider.setToolTip("Video Progress")
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderReleased.connect(lambda: self.setPosition(self.positionSlider.value()))

        # Create a QSlider for controlling the volume
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setFixedWidth(100)
        self.volumeSlider.setValue(self.defaultVolume)
        self.volumeSlider.sliderMoved.connect(self.set_volume)

        # Create a QPushButton for toggling mute/unmute sound
        self.muteUnmuteBtn = QPushButton()
        self.muteUnmuteBtn.clicked.connect(self.toggle_mute_unmute)
        self.muteUnmuteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.volumeSlider)
        controlLayout.addWidget(self.muteUnmuteBtn)

        layout = QVBoxLayout()
        layout.addLayout(layoutQVideoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")

    def playVideo(self):
        self.mediaPlayer.play()

    def stopVideo(self):
        self.mediaPlayer.stop()

    def updateVideo(self, videoPath):
        """
        Load a video file into the player.
        """
        fileName = videoPath

        if not fileName:
            return
        
        self.mediaPlayer.stop()
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
        self.playButton.setEnabled(True)
        self.statusBar.showMessage(fileName)

        self.togglePlayPause()
        self.positionSlider.setValue(0)

    def togglePlayPause(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    # @pyqtSlot()
    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    # @pyqtSlot()
    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    # @pyqtSlot()
    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    # @pyqtSlot(int)
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

    def cleanup(self):
        print("Cleanup VideoWidget")
        self.mediaPlayer.stop()
        self.positionSlider.setValue(0)
        self.playButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay)
        )
    
    def set_volume(self, volume):
        self.mediaPlayer.setVolume(volume)

    def toggle_mute_unmute(self):
        if self.mediaPlayer.volume() > 0:
            self.currentVolume = self.mediaPlayer.volume()
            self.mediaPlayer.setVolume(0)
            self.volumeSlider.setValue(0)
            self.muteUnmuteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            return
        else:
            self.mediaPlayer.setVolume(self.currentVolume)
            self.volumeSlider.setValue(self.currentVolume)
            self.muteUnmuteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            return
        
    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())
        self.mediaPlayer.stop()
        print(f"Error: " + self.mediaPlayer.errorString())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = self.graphicsView.size()
        self.videoItem.setSize(QSizeF(size.width()-30, size.height()-30))