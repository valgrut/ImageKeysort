from os import listdir
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QGraphicsDropShadowEffect, QStackedWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from src.EmptyGalleryWidget import EmptyGalleryImageWidget
from src.MediaContainerWidget import MediaContainerWidget


class GalleryManager(QStackedWidget):

    # TODO: presunout do EmptyGalleryWidget
    setSourceDirLabelTextSignal = pyqtSignal(str)

    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow  # TODO: sig-slots

        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setOffset(3, 3)
        shadowEffect.setBlurRadius(10)
        self.setGraphicsEffect(shadowEffect)

        # self.emptyInboxIcon.selectSourceSignal.connect(self.selectSourceDirectory)

        # Variables:
        self.availableMediaFiles = []
        self.galleryIndex = 0
        self.sourceDirectoryPath = ""

        #self.allowedSuffixes = ('.png', '.jpg', '.jpeg', '.webp')
        self.videoSuffixes = ("gif", "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm")  # TODO: spravit avi, zprovoznit mp4.
        self.allowedSuffixes = ('.png', '.jpg', '.jpeg', '.webp') + self.videoSuffixes  # TODO: spravit avi, zprovoznit mp4.

        # Stacked widgets:
        self.emptyInboxWidget = EmptyGalleryImageWidget()
        self.mediaContainerWidget = MediaContainerWidget(self)

        self.EMPTY_INBOX_WIDGET = 0
        self.MEDIA_WIDGET = 1

        self.addWidget(self.emptyInboxWidget)
        self.addWidget(self.mediaContainerWidget)

        self.setCurrentIndex(self.EMPTY_INBOX_WIDGET)
        print(f"[INIT] mediaContainerWidget: {id(self.mediaContainerWidget)}")

    def setSourcePath(self, path):
        self.sourceDirectoryPath = path
        self.mediaContainerWidget.setSourceDirLabelText(path)
        self.loadImagesInDirectory()

    def getSourcePath(self) -> str:
        return self.sourceDirectoryPath

    def selectSourceDirectory(self):
        srcPath = QFileDialog.getExistingDirectory(self.mainWindow, "Select source directory")
        if not srcPath:
            return
        self.sourceDirectoryPath = srcPath
        self.mediaContainerWidget.setSourceDirLabelText(self.sourceDirectoryPath)
        self.loadImagesInDirectory()

    def loadImagesInDirectory(self):
        if not self.sourceDirectoryPath:
            print("DEBUG: Error, src dir path is empty")
            return

        self.availableMediaFiles = []
        # self.images = [f for f in listdir(self.sourceDirectoryPath) if isfile(join(self.sourceDirectoryPath, f))]
        self.availableMediaFiles = [
            f for f in listdir(self.sourceDirectoryPath)
            if isfile(join(self.sourceDirectoryPath, f)) and f.lower().endswith(self.allowedSuffixes)
        ]
        self.availableMediaFiles.sort()
        self.galleryIndex = 0
        self.updatePreview()  # TODO

    def isGalleryEmpty(self):
        if not self.availableMediaFiles:
            return True
        return False

    def isCurrentVideo(self) -> bool:
        """
        returns true if current image is .gif or other video format
        """

        if str(self.availableMediaFiles[self.galleryIndex]).endswith(self.videoSuffixes):
            return True
        return False

    def getGalleryIndex(self):
        return self.galleryIndex

    def incrementGalleryIndex(self):
        if self.galleryIndex < len(self.availableMediaFiles) -1:
            self.galleryIndex += 1
        print(f"DBG: new gallery_index: {self.galleryIndex} out of {len(self.availableMediaFiles) - 1}")

    def decrementGalleryIndex(self):
        if self.galleryIndex >= 1:
            self.galleryIndex -= 1
        print(f"DBG: new gallery_index: {self.galleryIndex} out of {len(self.availableMediaFiles) - 1}")

    def setNextImage(self):
        self.incrementGalleryIndex()
        self.updatePreview()  # TODO: sig-slots

    def setPreviousImage(self):
        self.decrementGalleryIndex()
        self.updatePreview()  # TODO: sig-slots

    def setFirstImage(self):
        self.galleryIndex = 0
        self.updatePreview()  # TODO: sig-slots

    def setLastImage(self):
        self.galleryIndex = len(self.availableMediaFiles) - 1
        self.updatePreview()  # TODO: sig-slots

    def getCurrentFilename(self):
        if self.availableMediaFiles:
            return self.availableMediaFiles[self.galleryIndex]
        return ""

    def updateCounterLabelText(self):
        self.mediaContainerWidget.updateCounterLabelText(self.getCounterString())

    def updateFilenameLabelText(self):
        self.mediaContainerWidget.updateFilenameLabelText(self.getCurrentFilename())

    def updatePreview(self):
        # Cleanup current media
        # self.mediaContainerWidget.cleanupCurrentMedia()

        print(f"[CALL] GM: Updating mediaContainerWidget: {id(self.mediaContainerWidget)}")

        if self.isGalleryEmpty():
            self.setCurrentWidget(self.emptyInboxWidget)
            return

        if self.isCurrentVideo():
            print("DEBUG: Current file is video")
            # It is playable
            self.setCurrentWidget(self.mediaContainerWidget)
            self.mediaContainerWidget.setVideoWidget()

            videoPath = str(Path(self.sourceDirectoryPath + "/" + self.availableMediaFiles[self.galleryIndex]))
            self.mediaContainerWidget.updateVideo(videoPath) # Mozna spis prejmenovat na showVideo()
        else:
            print("DEBUG: Current file is an Image")
            # It is image
            self.setCurrentWidget(self.mediaContainerWidget)
            self.mediaContainerWidget.setImageWidget()

            imagePath = str(Path(self.sourceDirectoryPath + "/" + self.availableMediaFiles[self.galleryIndex]))
            self.mediaContainerWidget.updatePreviewImage(imagePath) # Mozna spis prejmenovat na showImage()

        self.updateFilenameLabelText()  # TODO: sig-slots
        self.updateCounterLabelText()  # TODO: sig-slots

        # Set focus to back to Gallery Manager so after adding shortcut, arrows still can be used to show next/previous image.
        self.setFocus()


    def getCounterString(self) -> str:
        counter = str(self.galleryIndex + 1) + "/" + str(len(self.availableMediaFiles))
        return counter

    def addFile(self, fileName, positionIndex=0):
        self.availableMediaFiles.insert(positionIndex, fileName)

    def removeFile(self, fileName):
        if fileName in self.availableMediaFiles:
            self.availableMediaFiles.remove(fileName)

        if self.galleryIndex >= len(self.availableMediaFiles):
            self.galleryIndex = len(self.availableMediaFiles) - 1
