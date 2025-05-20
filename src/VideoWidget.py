from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize, pyqtSlot
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

        scene = QGraphicsScene()
        graphicsView = QGraphicsView(scene)
        videoItem = QGraphicsVideoItem()
        graphicsView.setStyleSheet("border: 2px solid black;")
        # videoItem.setAspectRatioMode(Qt.KeepAspectRatio)
        scene.addItem(videoItem)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(videoItem)

        # self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        #self.qVideoWidget = QVideoWidget()
        # self.qVideoWidget.setAttribute(Qt.WA_OpaquePaintEvent, False)
        # self.qVideoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.mediaPlayer.setVideoOutput(self.qVideoWidget)
        
        layoutQVideoWidget = QVBoxLayout()
        # layoutQVideoWidget.addWidget(self.qVideoWidget, stretch=1)
        
        # TODO This causes problem, when uncommented:
        # layoutQVideoWidget.addWidget(self.qVideoWidget)
        layoutQVideoWidget.addWidget(graphicsView)
        
        btnSize = QSize(16, 16)

        self.playButton = QPushButton("Play")
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.togglePlayPause)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        # self.positionSlider.setMinimumHeight(20)
        # self.positionSlider.setMinimumWidth(100)
        # self.positionSlider.setTracking(False)
        # self.positionSlider.setTickInterval(5)
        # self.positionSlider.setTickPosition(QSlider.TicksBelow)
        self.positionSlider.setToolTip("Video Progress")
        # self.positionSlider.valueChanged.connect(self.mediaPlayer.position)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderReleased.connect(lambda: self.setPosition(self.positionSlider.value()))

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        # controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        # layout.addWidget(self.qVideoWidget)
        layout.addLayout(layoutQVideoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        # TODO: Pridat hlasitost / mute / unmute
        # TODO: fix size videa, aby se roztahlo pres cely rodicovsky widget, se zachovanim pomeru stran.

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
        self.positionSlider.setValue(0) # Reset the slider to 0

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
        # self.mediaPlayer.setMedia(QMediaContent())
        # self.videoWidget.close()
        # self.videoWidget.deleteLater()
        self.positionSlider.setValue(0)
        self.playButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay)
        )
    
    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())
        self.mediaPlayer.stop()
        print(f"Error: " + self.mediaPlayer.errorString())

    # def resizeEvent(self, event):
    #     # self.updateScaledPixmap()
    #     super().resizeEvent(event)
    #     self.repaint()