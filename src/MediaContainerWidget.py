import logging

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QStackedWidget, QLabel, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QMessageBox, \
    QVBoxLayout, QLineEdit

from src.ImageWidget import ImageWidget
from src.VideoWidget import VideoWidget
from src.Styles import Styles

# class ClickableLabel(QLabel):
#     def __init__(self, parent):
#         super().__init__(parent)
#
#     def mousePressEvent(self, event):
#         if not isinstance(event, QMouseEvent):
#             return
#         QMessageBox.about(self, "Hello!")

log = logging.getLogger(__name__)


class MediaContainerWidget(QWidget):
    def __init__(self, galleryManager):
        super().__init__()
        self.galleryManager = galleryManager  # toto dat pryc... nahradit za emit()

        self.imageViewWidget = ImageWidget()  # for .png, .jpg, ...
        self.videoViewWidget = VideoWidget()  # for .gif and such
        self.stackedMediaWidget = QStackedWidget()

        self.stackedMediaWidget.addWidget(self.imageViewWidget)
        self.stackedMediaWidget.addWidget(self.videoViewWidget)

        rightLayout = QVBoxLayout()

        self.sourceDirLabel = QLabel("No source directory selected. You can select one by pressing ctrl+L.")
        self.sourceDirLabel.setMaximumHeight(30)

        rightLayout.addWidget(self.sourceDirLabel)

        self.imageFilenameLabel = QLineEdit()
        self.imageFilenameLabel.setMaximumHeight(30)

        rightLayout.addWidget(self.imageFilenameLabel)
        rightLayout.addWidget(self.stackedMediaWidget)

        self.previousImageButton = QPushButton("&Previous", self)
        self.previousImageButton.clicked.connect(self.showPreviousImage)
        self.previousImageButton.setFocusPolicy(Qt.NoFocus)
        self.previousImageButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.previousImageButton.setFocus(True)
        self.previousImageButton.setGraphicsEffect(Styles.getShadowEffect())
        # self.previousImageButton.setIcon(QtGui.QIcon('Resources/Arrow_left'))
        # self.previousImageButton.setIconSize(QtCore.QSize(30, 30))

        self.nextImageButton = QPushButton("&Next", self)
        self.nextImageButton.clicked.connect(self.showNextImage)
        self.nextImageButton.setFocusPolicy(Qt.NoFocus)
        self.nextImageButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.nextImageButton.setFocus(True)
        self.nextImageButton.setGraphicsEffect(Styles.getShadowEffect())

        self.firstImageButton = QPushButton("&|<<", self)
        self.firstImageButton.clicked.connect(self.showFirstImage)
        self.firstImageButton.setFocusPolicy(Qt.NoFocus)
        self.firstImageButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.firstImageButton.setFocus(True)
        self.firstImageButton.setGraphicsEffect(Styles.getShadowEffect())

        self.lastImageButton = QPushButton("&>>|", self)
        self.lastImageButton.clicked.connect(self.showLastImage)
        self.lastImageButton.setFocusPolicy(Qt.NoFocus)
        self.lastImageButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.lastImageButton.setFocus(True)
        self.lastImageButton.setGraphicsEffect(Styles.getShadowEffect())

        self.imageCounterLabel = QLabel()
        self.imageCounterLabel.setText("0/0")

        rightControlButtonsLayout = QHBoxLayout()
        rightControlButtonsLayout.addWidget(self.firstImageButton)
        rightControlButtonsLayout.addWidget(self.previousImageButton)
        rightControlButtonsLayout.addStretch()
        rightControlButtonsLayout.addWidget(self.imageCounterLabel)
        rightControlButtonsLayout.addStretch()
        rightControlButtonsLayout.addWidget(self.nextImageButton)
        rightControlButtonsLayout.addWidget(self.lastImageButton)

        rightLayout.addLayout(rightControlButtonsLayout)

        self.setLayout(rightLayout)

        # Update Counter label
        self.imageCounterLabel.setText(self.galleryManager.getCounterString())

        # Show ImageViewWidget by default
        # self.stackedMediaWidget.setCurrentWidget(self.imageViewWidget)


    def setCopyModeBorderHighlight(self):
        # print(self.stackedMediaWidget.currentWidget().styleSheet())
        self.stackedMediaWidget.currentWidget().setStyleSheet(f"""
            border: 5px solid orange;
        """)
        # self.stackedMediaWidget.currentWidget().setProperty("copyMode", True)
        # self.stackedMediaWidget.currentWidget().style().unpolish(self.stackedMediaWidget.currentWidget())
        # self.stackedMediaWidget.currentWidget().style().polish(self.stackedMediaWidget.currentWidget())
        # self.stackedMediaWidget.update()

    def unsetCopyModeBorderHighlight(self):
        self.stackedMediaWidget.currentWidget().setStyleSheet(f"""
            border: none;
        """)
        # self.stackedMediaWidget.currentWidget().setProperty("copyMode", False)

    def cleanupCurrentMedia(self):
        current = self.stackedMediaWidget.currentWidget()
        if current == self.videoViewWidget:
            self.videoViewWidget.cleanup()

    def showNextImage(self):
        self.cleanupCurrentMedia()
        self.galleryManager.setNextImage()
        # self.imageCounterLabel.setText(self.galleryManager.getCounterString())

    def showPreviousImage(self):
        self.cleanupCurrentMedia()
        self.galleryManager.setPreviousImage()
        # self.imageCounterLabel.setText(self.galleryManager.getCounterString())

    def showFirstImage(self):
        self.cleanupCurrentMedia()
        self.galleryManager.setFirstImage()
        self.imageCounterLabel.setText(self.galleryManager.getCounterString())

    def showLastImage(self):
        self.cleanupCurrentMedia()
        self.galleryManager.setLastImage()
        self.imageCounterLabel.setText(self.galleryManager.getCounterString())

    def setVideoWidget(self):
        self.stackedMediaWidget.setCurrentWidget(self.videoViewWidget)

    def setImageWidget(self):
        self.stackedMediaWidget.setCurrentWidget(self.imageViewWidget)

    def updateCounterLabelText(self, text):
        self.imageCounterLabel.setText(text)

    def updateFilenameLabelText(self, text):
        self.imageFilenameLabel.setText(text)

    def setSourceDirLabelText(self, path: str):
        self.sourceDirLabel.setText(path)

    def updateVideo(self, videoPath):
        self.videoViewWidget.updateVideo(videoPath)

    def updatePreviewImage(self, path):
        self.imageViewWidget.updateImage(path)
