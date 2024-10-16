from os import listdir
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QFileDialog

from ImageWidget import ImageWidget
from EmptyGalleryImageLabel import EmptyGalleryImageLabel

class GalleryManager():

    setSourceDirLabelTextSignal = pyqtSignal(str)

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow # TODO: sig-slots
        self.images = []
        self.galleryIndex = 0
        self.sourceDirectoryPath = ""
        self.imageView = ImageWidget()  # for .png, .jpg, ...
        self.videoView = QMovie()  # for .gif and such

        self.emptyInboxLabel = EmptyGalleryImageLabel()
        self.emptyInboxLabel.setFocus(False)
        self.emptyInboxLabel.setStyleSheet("border: 1px solid black;")
        # self.emptyInboxIcon.selectSourceSignal.connect(self.selectSourceDirectory)

    def getSuitableLabel(self):
        """
        Return such label based on the gallery state (empty vs non-empty..)
        """
        if self.isGalleryEmpty():
            return self.emptyInboxLabel
        else:
            return self.imageView

    def mousePressEvent(self, ev):
        self.clicked.emit()

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
        self.updatePreview(self.mainWindow.previewLabel)  # TODO

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

    def setNextImage(self, viewLabel):
        self.incrementGalleryIndex()
        self.updatePreview(viewLabel) # TODO: sig-slots

    def setPreviousImage(self, viewLabel):
        self.decrementGalleryIndex()
        self.updatePreview(viewLabel) # TODO: sig-slots

    def getCurrentFilename(self):
        if self.images:
            return self.images[self.galleryIndex]
        return ""

    # TODO: previewLabel pryc, misto toho signal-slot
    def updatePreview(self, previewLabel):
        if self.isGalleryEmpty():
            # TODO: sets something containing clickable board to open and set new source Directory.
            # self.previewLabel = ...?
            # previewLabel.setPixmap(self.emptyInboxIcon)
            # previewLabel.addWidget(self.emptyInboxIcon)
            previewLabel = self.getSuitableLabel()
            return

        if self.isCurrentVideo():
            # It is playable
            self.videoView.setFileName(str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))
            previewLabel.setMovie(self.videoView)
            self.videoView.start()

        else:
            # It is image
            print(str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))
            self.imageView.updateImage(str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))
            previewLabel.setPixmap(self.imageView.pixmap)

        self.mainWindow.image_filename_label.setText(self.getCurrentFilename()) # TODO: sig-slots
        self.mainWindow.image_counter_label.setText(self.getCounterString()) # TODO: sig-slots

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