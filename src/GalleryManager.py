from os import listdir
from os.path import isfile, join
from pathlib import Path
import logging

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QMimeDatabase
from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsDropShadowEffect, QStackedWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from src.EmptyGalleryWidget import EmptyGalleryImageWidget
from src.MediaContainerWidget import MediaContainerWidget

log = logging.getLogger(__name__)

class GalleryManager(QStackedWidget):

    # TODO: presunout do EmptyGalleryWidget
    setSourceDirLabelTextSignal = pyqtSignal(str)
    disableExtractTextButtonSignal = pyqtSignal()
    enableExtractTextButtonSignal = pyqtSignal()
    disableCropButtonSignal = pyqtSignal()
    enableCropButtonSignal = pyqtSignal()

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
        self.textSuffixes = (".txt", ".log", ".csv", ".ini", ".json", ".xml", ".md", ".yaml", ".yml", ".py", ".cpp", ".c", ".h", ".html", ".htm", ".css", ".js")  # TODO: presunout do Settings a pridat dalsi text formaty (nebo to udelat nejak genericky)
        self.videoSuffixes = ("gif", "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm")  # TODO: presunout do Settings; spravit avi, zprovoznit mp4.
        self.allowedSuffixes = ('.png', '.jpg', '.jpeg', '.webp') + self.videoSuffixes  + self.textSuffixes # TODO: presunout do Settings; spravit avi, zprovoznit mp4.

        # Stacked widgets:
        self.emptyInboxWidget = EmptyGalleryImageWidget()
        self.mediaContainerWidget = MediaContainerWidget(self)

        self.EMPTY_INBOX_WIDGET = 0
        self.MEDIA_WIDGET = 1

        self.addWidget(self.emptyInboxWidget)
        self.addWidget(self.mediaContainerWidget)

        self.setCurrentIndex(self.EMPTY_INBOX_WIDGET)
        # log.info(f"[INIT] mediaContainerWidget: {id(self.mediaContainerWidget)}")

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
            log.info("DEBUG: Error, src dir path is empty")
            return

        self.availableMediaFiles = []
        # self.images = [f for f in listdir(self.sourceDirectoryPath) if isfile(join(self.sourceDirectoryPath, f))]
        # TODO: Refactor this to only include allowed file types based on enabled types in Settings.
        self.availableMediaFiles = [
            f for f in listdir(self.sourceDirectoryPath)
            if isfile(join(self.sourceDirectoryPath, f)) and (f.lower().endswith(self.allowedSuffixes) or self.isCurrentTextFile(join(self.sourceDirectoryPath, f)))
        ]
        self.availableMediaFiles.sort()
        self.galleryIndex = 0
        self.updatePreview()  # TODO

    def isGalleryEmpty(self):
        if not self.availableMediaFiles:
            return True
        return False

    def isCurrentTextFile(self, path=None) -> bool:
        """
        returns true if current file is .txt or other text format
        """

        db = QMimeDatabase()
        if path is None:
            path = str(Path(self.sourceDirectoryPath + "/" + self.getCurrentFilename()))
        
        # 1) by filename (fast; catches Makefile, Dockerfile, etc. on many systems)
        # mt = db.mimeTypeForFile(path, QMimeDatabase.MatchExtension)
        # if mt.name().startswith("text/"):
        #     return True

        # 2) by content (slower; best for “no suffix” or wrong suffix)
        mt = db.mimeTypeForFile(path, QMimeDatabase.MatchContent)
        if mt.name().startswith("text/"):
            log.info(f"Preview file: {self.getCurrentFilename()} of the type: {QMimeDatabase().mimeTypeForFile(self.getCurrentFilename()).name()}")
            return True

        # sometimes scripts/configs come as application/x-... but are still text
        if mt.inherits("text/plain"):
            log.info(f"Preview file: {self.getCurrentFilename()} of the type: {QMimeDatabase().mimeTypeForFile(self.getCurrentFilename()).name()}")
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
        # log.info(f"DBG: new gallery_index: {self.galleryIndex} out of {len(self.availableMediaFiles) - 1}")

    def decrementGalleryIndex(self):
        if self.galleryIndex >= 1:
            self.galleryIndex -= 1
        # log.info(f"DBG: new gallery_index: {self.galleryIndex} out of {len(self.availableMediaFiles) - 1}")

    @pyqtSlot()
    def setNextImage(self):
        self.incrementGalleryIndex()
        self.updatePreview()  # TODO: sig-slots

    @pyqtSlot()
    def setPreviousImage(self):
        self.decrementGalleryIndex()
        self.updatePreview()  # TODO: sig-slots

    @pyqtSlot()
    def setFirstImage(self):
        self.galleryIndex = 0
        self.updatePreview()  # TODO: sig-slots

    @pyqtSlot()
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

        if self.isGalleryEmpty():
            self.setCurrentWidget(self.emptyInboxWidget)
            return

        # TODO: Refactor this method to somethink like this:
        # if ext in (".txt", ".log", ".md", ".py", ".json", ".yaml", ".yml", ".ini"):
        # if ext == ".pdf":
        # if .......

        if self.isCurrentVideo():
            # It is playable
            self.setCurrentWidget(self.mediaContainerWidget)
            self.mediaContainerWidget.setVideoWidget()
            
            videoPath = str(Path(self.sourceDirectoryPath + "/" + self.availableMediaFiles[self.galleryIndex]))
            self.mediaContainerWidget.updateVideo(videoPath)  # Mozna spis prejmenovat na showVideo()
            self.disableExtractTextButtonSignal.emit()
            self.enableCropButtonSignal.emit()
        
        #elif self.getCurrentFilename().lower().endswith(self.textSuffixes):
        elif self.isCurrentTextFile():
            # It is text file
            self.setCurrentWidget(self.mediaContainerWidget)
            self.mediaContainerWidget.setTextWidget()

            textFilePath = str(Path(self.sourceDirectoryPath + "/" + self.availableMediaFiles[self.galleryIndex]))
            self.mediaContainerWidget.updateTextFile(textFilePath)
            self.disableExtractTextButtonSignal.emit()
            self.disableCropButtonSignal.emit()
        
        else:
            # It is image
            self.setCurrentWidget(self.mediaContainerWidget)
            self.mediaContainerWidget.setImageWidget()
            self.enableExtractTextButtonSignal.emit()
            self.enableCropButtonSignal.emit()

            imagePath = str(Path(self.sourceDirectoryPath + "/" + self.availableMediaFiles[self.galleryIndex]))
            self.mediaContainerWidget.updatePreviewImage(imagePath)  # Mozna spis prejmenovat na showImage()

        self.updateFilenameLabelText()  # TODO: sig-slots
        self.updateCounterLabelText()  # TODO: sig-slots

        # Set focus to back to Gallery Manager so after adding shortcut, arrows still can be used to show next/previous image.
        self.setFocus()


    def getCounterString(self) -> str:
        counter: str = str(self.galleryIndex + 1) + "/" + str(len(self.availableMediaFiles))
        return counter

    def addFile(self, fileName, positionIndex=0):
        self.availableMediaFiles.insert(positionIndex, fileName)

    def removeFile(self, fileName):
        if fileName in self.availableMediaFiles:
            self.availableMediaFiles.remove(fileName)

        if self.galleryIndex >= len(self.availableMediaFiles):
            self.galleryIndex = len(self.availableMediaFiles) - 1
