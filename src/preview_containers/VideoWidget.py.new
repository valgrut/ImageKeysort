import logging
import pathlib

from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSlot, pyqtSignal, QSizeF
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtWidgets import (QHBoxLayout, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar,
                             QLabel, QGraphicsScene, QGraphicsView)

from src.GalleryItem import GalleryItem
from src.SettingsDialog import SettingsDialog
from src.Styles import Styles

log = logging.getLogger(__name__)


# VideoViewWidget (Nic spolecneho s QVideoWidget)
class VideoWidget(QWidget):

    updateUISignal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.videoURL = ""

        self.defaultVolume = 50

        self.videoScene = QGraphicsScene(self)
        self.videoScene.setBackgroundBrush(QBrush(QColor("blue")))

        self.videoView = QGraphicsView(self.videoScene, self)
        self.videoView.setMinimumSize(320, 240)
        self.videoView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.videoView.setFrameShape(QGraphicsView.NoFrame)
        self.videoView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.videoView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.videoView.setAlignment(Qt.AlignCenter)

        self.videoItem = QGraphicsVideoItem()
        self.videoItem.setPos(0, 0)
        self.videoItem.show()
        self.videoScene.addItem(self.videoItem)

        self.mediaPlayer = QMediaPlayer(self)
        self.mediaPlayer.setVideoOutput(self.videoItem)

        # self.mediaPlayer = QMediaPlayer(self)
        # self.mediaPlayer.setVideoOutput(self.videoWidget)
        # self.mediaPlayer.setVolume(self.defaultVolume)

        btnSize = QSize(16, 16)

        self.playButton = QPushButton("Play")
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.togglePlayPause)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 100)
        # self.positionSlider.setTickInterval(3)
        # self.positionSlider.setTickPosition(QSlider.TicksLeft)
        self.positionSlider.setToolTip("Video Progress")
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderReleased.connect(lambda: self.setPosition(self.positionSlider.value()))
        # self.positionSlider.setTracking(True)
        # self.positionSlider.setMouseTracking(True)
        # self.positionSlider.setUpdatesEnabled(True)
        # self.setUpdatesEnabled(True)

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

        self.statusBar = QLabel()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.volumeSlider)
        controlLayout.addWidget(self.muteUnmuteBtn)

        layout = QVBoxLayout()
        # layout.addWidget(self.videoWidget)
        layout.addWidget(self.videoView)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.mediaPlayer.mediaStatusChanged.connect(self.mediaStatusChanged)

        self.statusBar.setText("Ready")

    def playVideo(self):
        self.mediaPlayer.play()

    def stopVideo(self):
        self.mediaPlayer.stop()

    def updateVideo(self, videoPath: GalleryItem):
        """
        Load a video file into the player.
        """
        fileName: str = videoPath.pathAsStr()

        if not fileName:
            log.warning("Empty video path.")
            return

        self.mediaPlayer.stop()

        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
        self.playButton.setEnabled(True)
        self.statusBar.setText(fileName)

        self.updateVideoItemGeometry()

        if SettingsDialog.settingsGetMuteDefault():
            self.setMuted()

        # self.togglePlayPause()
        self.positionSlider.setValue(0)

        self.updateVideoItemGeometry()

        self.videoView.viewport().update()
        self.videoView.update()
        self.videoScene.update()

        self.playVideo()


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
        log.debug(f"positionChanged: {position}.")
        if not self.positionSlider.isSliderDown():
            self.positionSlider.setValue(position)
        # self.positionSlider.update()
        # self.positionSlider.repaint()
        # self.updateUISignal.emit()

    # @pyqtSlot()
    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        # self.positionSlider.update()

    # @pyqtSlot(int)
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def cleanup(self):
        log.info("Cleanup VideoWidget")
        self.mediaPlayer.stop()
        self.positionSlider.setValue(0)
        self.playButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay)
        )

    def set_volume(self, volume):
        self.mediaPlayer.setVolume(volume)

    def setMuted(self):
        self.currentVolume = self.mediaPlayer.volume()
        self.mediaPlayer.setVolume(0)
        self.volumeSlider.setValue(0)
        self.muteUnmuteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        return

    def setUnmuted(self):
        self.mediaPlayer.setVolume(self.currentVolume)
        self.volumeSlider.setValue(self.currentVolume)
        self.muteUnmuteBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        return

    def toggle_mute_unmute(self):
        if self.mediaPlayer.volume() > 0:
            self.setMuted()
        else:
            self.setUnmuted()

    def handleError(self, error=None):
        self.playButton.setEnabled(False)
        self.statusBar.setText("Error: " + self.mediaPlayer.errorString())
        self.mediaPlayer.stop()
        # log.info(f"Error: {self.mediaPlayer.errorString()}")
        log.error(
            "QMediaPlayer error: enum=%s, text=%r, media=%s",
            error,
            self.mediaPlayer.errorString(),
            self.mediaPlayer.currentMedia().canonicalUrl().toString()
        )

    def mediaStatusChanged(self, status):
        log.info(
            "Media status changed: status=%s, error=%s, errorString=%r",
            status,
            self.mediaPlayer.error(),
            self.mediaPlayer.errorString()
        )

    def updateVideoItemGeometry(self):
        if not hasattr(self, "videoItem"):
            return

        viewport_size = self.videoView.viewport().size()
        log.debug(
            "video geometry: view=%s viewport=%s item-size=%s scene=%s",
            self.videoView.size(),
            viewport_size,
            self.videoItem.size(),
            self.videoScene.sceneRect(),
        )
        if viewport_size.width() <= 0 or viewport_size.height() <= 0:
            return

        target_size = QSizeF(viewport_size.width(), viewport_size.height())

        self.videoItem.setSize(target_size)
        self.videoScene.setSceneRect(0, 0, target_size.width(), target_size.height())
        self.videoItem.setPos(0, 0)

        log.debug(
            "video geometry after: item-size=%s scene=%s",
            self.videoItem.size(),
            self.videoScene.sceneRect(),
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        #
        # if hasattr(self, "videoItem") and hasattr(self, "videoView"):
        #     size = self.videoView.viewport().size()
        #     self.videoItem.setSize(QSizeF(size.width(), size.height()))
        #     # self.videoView.fitInView(self.videoItem, Qt.KeepAspectRatio)

        self.updateVideoItemGeometry()