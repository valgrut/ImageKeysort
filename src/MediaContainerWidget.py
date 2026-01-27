import logging
import os
from pathlib import Path

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject, QSize, QRect
from PyQt5.QtGui import QCursor, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QStackedWidget, QLabel, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QMessageBox, \
    QVBoxLayout, QLineEdit

from src.ImageWidget import ImageWidget
from src.VideoWidget import VideoWidget
from src.TextPreviewWidget import TextPreviewWidget
from src.Styles import Styles

from src.CropData import CropData


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

    pushCropCommandRequestCommand = pyqtSignal(CropData)
    repeatCropCommandSignal = pyqtSignal(QSize, QRect)
    rotateImageSignal = pyqtSignal()

    def __init__(self, galleryManager):
        super().__init__()
        self.galleryManager = galleryManager  # toto dat pryc... nahradit za emit()

        self.imageViewWidget = ImageWidget()  # for .png, .jpg, ...
        self.videoViewWidget = VideoWidget()  # for .gif and such
        self.textPreviewWidget = TextPreviewWidget()
        self.stackedMediaWidget = QStackedWidget()

        self.stackedMediaWidget.addWidget(self.imageViewWidget)
        self.stackedMediaWidget.addWidget(self.videoViewWidget)
        self.stackedMediaWidget.addWidget(self.textPreviewWidget)

        rightLayout = QVBoxLayout()

        self.sourceDirLabel = QLabel()
        self.sourceDirLabel.setMaximumHeight(30)

        rightLayout.addWidget(self.sourceDirLabel)

        self.imageFilenameField = QStackedWidget()
        self.imageFilenameField.setMaximumHeight(30)
        self.imageFilenameEdit = QLineEdit()
        self.imageFilenameLabel = QLabel()
        self.imageFilenameLabel.mouseDoubleClickEvent = lambda event: self.startFilenameEdit()
        self.imageFilenameField.addWidget(self.imageFilenameLabel)
        self.imageFilenameField.addWidget(self.imageFilenameEdit)
        self.imageFilenameField.setCurrentWidget(self.imageFilenameLabel)

        rightLayout.addWidget(self.imageFilenameField)
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

        # Connect signals
        self.imageViewWidget.pushCropCommandRequestCommand.connect(self.pushCropCommandRequestCommand)  # Re-emit signal
        self.repeatCropCommandSignal.connect(self.imageViewWidget.repeatCropCommandSlot)
        self.rotateImageSignal.connect(self.imageViewWidget.rotateImage)
        

    # def getOriginalImageSize(self) -> QSize:
    #     self.imageViewWidget.getOriginalImageSize()


    def keyPressEvent(self, a0):
        """
        Handle key press events for filename editing.

        :param a0: QKeyEvent
        """
        if isinstance(a0, QKeyEvent):
            if a0.key() == Qt.Key_Return or a0.key() == Qt.Key_Enter:
                self.finishFilenameEdit()
                return
            if a0.key() == Qt.Key_Escape:
                self.quitFilenameEdit()
                return
        return super().keyPressEvent(a0)

    @pyqtSlot()
    def startFilenameEdit(self):
        """
        Start filename edit process.
        """
        self.imageFilenameField.setCurrentWidget(self.imageFilenameEdit)
        self.imageFilenameEdit.setText(self.galleryManager.getCurrentFilename())
        self.imageFilenameEdit.setFocus()
        #self.imageFilenameEdit.selectAll()  # TODO: Select all but file extension
        self.imageFilenameEdit.setSelection(0, len(self.galleryManager.getCurrentFilename()) - len(Path(self.galleryManager.getCurrentFilename()).suffix))

    @pyqtSlot()
    def finishFilenameEdit(self):
        """
        Finish filename edit and save changes.
        """
        self.galleryManager.commitNewFileName(self.imageFilenameEdit.text())
        self.imageFilenameField.setCurrentWidget(self.imageFilenameLabel)
        self.galleryManager.setFocus()

    def quitFilenameEdit(self):
        """
        Quit filename edit without saving changes.
        """
        self.imageFilenameField.setCurrentWidget(self.imageFilenameLabel)
        self.galleryManager.setFocus()

    def setCopyModeBorderHighlight(self):
        """
        Set border highlight for copy mode.
        """
        # print(self.stackedMediaWidget.currentWidget().styleSheet())
        self.stackedMediaWidget.currentWidget().setStyleSheet(f"""
            border: 5px solid orange;
        """)
        # self.stackedMediaWidget.currentWidget().setProperty("copyMode", True)
        # self.stackedMediaWidget.currentWidget().style().unpolish(self.stackedMediaWidget.currentWidget())
        # self.stackedMediaWidget.currentWidget().style().polish(self.stackedMediaWidget.currentWidget())
        # self.stackedMediaWidget.update()

    def unsetCopyModeBorderHighlight(self):
        """
        Unset border highlight for copy mode.
        """
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
    
    def setTextWidget(self):
        self.stackedMediaWidget.setCurrentWidget(self.textPreviewWidget)


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
    
    def updateTextFile(self, path: str):
        self.textPreviewWidget.setTextFile(path)
