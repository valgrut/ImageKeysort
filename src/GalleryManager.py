from os import listdir
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QGraphicsDropShadowEffect, QStackedWidget

from VideoWidget import VideoWidget
from ImageWidget import ImageWidget
from EmptyGalleryWidget import EmptyGalleryImageWidget


class GalleryManager(QStackedWidget):

    # TODO: presunout do EmptyGalleryWidget
    setSourceDirLabelTextSignal = pyqtSignal(str)

    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow  # TODO: sig-slots


        self.shadowEffect = QGraphicsDropShadowEffect()
        self.shadowEffect.setOffset(3, 3)
        self.shadowEffect.setBlurRadius(10)
        self.setGraphicsEffect(self.shadowEffect)

        # self.emptyInboxIcon.selectSourceSignal.connect(self.selectSourceDirectory)

        # Variables:
        self.images = []
        self.galleryIndex = 0
        self.sourceDirectoryPath = ""

        # TODO: Semka mozna presunout sourceDirLabel a ImageNameLabel.

        # Stacked widgets:
        self.emptyInboxWidget = EmptyGalleryImageWidget()
        self.imageViewWidget = ImageWidget()  # for .png, .jpg, ...
        self.videoViewWidget = VideoWidget()  # for .gif and such

        # TODO A tyhle styly nudou genericke, ne jen pro emptyimage... Mozna udelat nejakou factory, ktera by podle podminek davala spravnej objekt sem.

        self.EMPTY_INBOX_WIDGET = 0
        self.IMAGE_WIDGET = 1
        self.VIDEO_WIDGET = 2

        self.addWidget(self.emptyInboxWidget)
        self.addWidget(self.imageViewWidget)
        self.addWidget(self.videoViewWidget)

        self.setCurrentIndex(self.EMPTY_INBOX_WIDGET)

    def setSourcePath(self, path):
        self.sourceDirectoryPath = path
        self.mainWindow.source_dir_label.setText(path)  # TODO: sig-slots, replace this.
        #self.setSourceDirLabelTextSignal.emit(path)  # TODO: for this.
        self.loadImagesInDirectory()

    def getSourcePath(self) -> str:
        return self.sourceDirectoryPath

    def selectSourceDirectory(self):
        srcPath = QFileDialog.getExistingDirectory(self.mainWindow, "Select source directory")
        if not srcPath:
            return
        self.sourceDirectoryPath = srcPath
        self.mainWindow.source_dir_label.setText(self.sourceDirectoryPath) # TODO: sig-slots
        self.loadImagesInDirectory()

    def loadImagesInDirectory(self):
        if not self.sourceDirectoryPath:
            print("DEBUG: Error, src dir path is empty")
            return

        self.images = []
        # self.images = [f for f in listdir(self.sourceDirectoryPath) if isfile(join(self.sourceDirectoryPath, f))]
        self.images = [
            f for f in listdir(self.sourceDirectoryPath)
            if isfile(join(self.sourceDirectoryPath, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        ]
        self.images.sort()
        self.galleryIndex = 0
        self.updatePreview()  # TODO

    def isGalleryEmpty(self):
        if not self.images:
            return True
        return False

    def isCurrentVideo(self) -> bool:
        """
        returns true if current image is .gif or other video format
        """
        videoSuffixes = ("gif", "mp4", "avi")
        if str(self.images[self.galleryIndex]).endswith(videoSuffixes):
            return True
        return False

    def getGalleryIndex(self):
        return self.galleryIndex

    def incrementGalleryIndex(self):
        if self.galleryIndex < len(self.images) -1:
            self.galleryIndex += 1
        print(f"DBG: new gallery_index: {self.galleryIndex} out of {len(self.images) - 1}")

    def decrementGalleryIndex(self):
        if self.galleryIndex >= 1:
            self.galleryIndex -= 1
        print(f"DBG: new gallery_index: {self.galleryIndex} out of {len(self.images) - 1}")

    def setNextImage(self):
        self.incrementGalleryIndex()
        self.updatePreview() # TODO: sig-slots

    def setPreviousImage(self):
        self.decrementGalleryIndex()
        self.updatePreview() # TODO: sig-slots

    def getCurrentFilename(self):
        if self.images:
            return self.images[self.galleryIndex]
        return ""

    # TODO: previewLabel pryc, misto toho signal-slot
    def updatePreview(self):
        if self.isGalleryEmpty():
            # TODO: sets something containing clickable board to open and set new source Directory.
            # self.previewLabel = ...?
            # previewLabel.setPixmap(self.emptyInboxIcon)
            # previewLabel.addWidget(self.emptyInboxIcon)
            # previewLabel = self.getSuitableLabel()
            self.setCurrentIndex(self.EMPTY_INBOX_WIDGET)
            return

        if self.isCurrentVideo():
            # It is playable
            self.setCurrentIndex(self.VIDEO_WIDGET)
            self.videoViewWidget.setFileName(str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))
            self.videoViewWidget.setMovie(self.videoViewWidget)
            self.videoViewWidget.start()

        else:
            # It is image
            self.setCurrentIndex(self.IMAGE_WIDGET)
            print("DEBUG:" + str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))
            self.imageViewWidget.updateImage(str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))

        self.mainWindow.image_filename_label.setText(self.getCurrentFilename())  # TODO: sig-slots
        self.mainWindow.image_counter_label.setText(self.getCounterString())  # TODO: sig-slots

    def getCounterString(self) -> str:
        counter = str(self.galleryIndex + 1) + "/" + str(len(self.images))
        return counter

    def addFile(self, fileName, positionIndex=0):
        self.images.insert(positionIndex, fileName)

    def removeFile(self, fileName):
        if fileName in self.images:
            self.images.remove(fileName)

        if self.galleryIndex >= len(self.images):
            self.galleryIndex = len(self.images) - 1