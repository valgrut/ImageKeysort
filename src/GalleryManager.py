from os import listdir
from os.path import isfile, join
from pathlib import Path
import logging

from PyQt5 import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QMimeDatabase, QSize, QRect
from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsDropShadowEffect, QStackedWidget, QRubberBand
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from src.EmptyGalleryWidget import EmptyGalleryImageWidget
from src.MediaContainerWidget import MediaContainerWidget
from src.CropData import CropData


log = logging.getLogger(__name__)

class GalleryManager(QStackedWidget):

    # TODO: presunout do EmptyGalleryWidget
    setSourceDirLabelTextSignal = pyqtSignal(str)
    disableExtractTextButtonSignal = pyqtSignal()
    enableExtractTextButtonSignal = pyqtSignal()
    disableCropButtonSignal = pyqtSignal()
    enableCropButtonSignal = pyqtSignal()
    setFilenameTextEditSignal = pyqtSignal()
    updateStatusBarLabelSignal = pyqtSignal(str)
    pushCropCommandRequestCommand = pyqtSignal(CropData)
    repeatCropCommandSignal = pyqtSignal(QSize, QRect)
    rotateImageSignal = pyqtSignal()


    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow  # TODO: sig-slots

        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setOffset(3, 3)
        shadowEffect.setBlurRadius(10)
        self.setGraphicsEffect(shadowEffect)

        # Enable drag and drop of directory from outside of this app
        self.setAcceptDrops(True)

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

        self.mediaContainerWidget.pushCropCommandRequestCommand.connect(self.pushCropCommandRequestCommand)  # Re-emit signal
        self.mainWindow.updateMediaPreviewSignal.connect(self.updatePreview)
        self.mainWindow.repeatCropCommandSignal.connect(self.mediaContainerWidget.repeatCropCommandSignal)
        # self.rotateImageSignal.connect(self.mediaContainerWidget.rotateImageSignal)


    def setSourcePath(self, path: str):
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
        """
        returns true if there is no media files in the gallery.
        """
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
        returns true if current file (given by self.galleryIndex) is a video.
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
        self.updatePreview()  # TODO: sig-slots ?

    @pyqtSlot()
    def setPreviousImage(self):
        self.decrementGalleryIndex()
        self.updatePreview()  # TODO: sig-slots ?

    @pyqtSlot()
    def setFirstImage(self):
        self.galleryIndex = 0
        self.updatePreview()  # TODO: sig-slots ?

    @pyqtSlot()
    def setLastImage(self):
        self.galleryIndex = len(self.availableMediaFiles) - 1
        self.updatePreview()  # TODO: sig-slots ?

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

    @pyqtSlot()
    def renameFile(self):
        """
        Starts the filename edit process.
        """
        self.setFilenameTextEditSignal.emit()
        self.mediaContainerWidget.startFilenameEdit()

    @pyqtSlot()
    def rotateImageRight(self):
        """
        Rotates the current image 90 degrees to the right.
        """
        print("rotateImageRight called")
        # self.rotateImageSignal.emit()
        self.mediaContainerWidget.rotateImageSignal.emit()
        self.updatePreview()

    
    def commitNewFileName(self, newFileName):
        """
        Commits the new filename to the gallery's availableMediaFiles list.
        """
        originalFilename = self.getCurrentFilename()

        originalFullPath = Path(self.getSourcePath() + "/" + originalFilename)
        newFullPath = Path(self.getSourcePath() + "/" + newFileName)

        log.info(f"Original full path: {originalFullPath}")
        log.info(f"new full path: {newFullPath}")

        # TODO [ ] Validate new filename (no special chars etc.)

        # Check that new filename is not empty (or just suffix)
        # TODO

        # Check whether the file with the such name already exists
        if newFullPath.exists():
            self.updateStatusBarLabelSignal.emit("Error: A file with such name already exists.")
            log.info("Error: A file with such name already exists.")
            return
        
        # Check if the file is different and if the new name is not empty
        if newFileName and newFileName != originalFilename:
            self.availableMediaFiles[self.galleryIndex] = newFileName
            self.updateFilenameLabelText()
            originalFullPath.rename(newFullPath)
            self.updateStatusBarLabelSignal.emit("File was renamed successfully.")
            log.info("File was renamed successfully.")


    def appendTagToName(self, tag: str = None):
        currentFilePath = Path(self.getCurrentFilename())
        currentFileNameNoExt = currentFilePath.stem
        currentSrcDirPath = currentFilePath.parent
        extension = currentFilePath.suffix
        currentFile = currentFilePath.name

        # A) Test tag appending
        # if tag is None:
        #     if "[Tag1]" in currentFileNameNoExt:
        #         log.info("Filename already contains the tag.")
        #         return
            
        #     tagged = currentFileNameNoExt + " [Tag1]" + extension
        #     log.info(f"Appending tag to filename: {tagged}")

        #     # TODO: Add command into stack so it can be Undone.
        #     return
        
        # B) Production version:
        if tag is None or tag in currentFileNameNoExt:
            log.info(f"Filename already contains the tag '[{tag}]'.")
            return
        
        nameWithTag = f"{currentFileNameNoExt} [{tag}]{extension}"
        log.info(f"Appending tag to filename: {nameWithTag}")

        # TODO: Add command into stack so it can be Undone.

        # Commit new filename
        self.commitNewFileName(nameWithTag)
        
        return


    def removeFile(self, fileName):
        if fileName in self.availableMediaFiles:
            self.availableMediaFiles.remove(fileName)

        if self.galleryIndex >= len(self.availableMediaFiles):
            self.galleryIndex = len(self.availableMediaFiles) - 1


    def dragEnterEvent(self, event) -> None:
        """
        Enables drag and drop of directory from the outside of an app and set it as source directory.
        :param event:
        :return:
        """
        if event.mimeData().hasUrls:
            event.accept()
            # log.info(f"Drag enter: Has URL")
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls:
            event.accept()
            # log.info(f"Drag Move: Has URL")
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls:
            log.info(f"{event.mimeData().urls()}")
            directory_uri = Path(event.mimeData().urls()[0].toLocalFile())
            if not directory_uri.is_dir():
                log.info(f"Dropped file {directory_uri} is not directory.")
                self.updateStatusBarLabelSignal.emit(f"Dropped file {directory_uri} is not directory.")
                return
            log.info(f"Successful drop - Opening a directory {directory_uri} as gallery source.")
            self.updateStatusBarLabelSignal.emit(f"Successful drop - Opening a directory {directory_uri} as gallery source.")
            # TODO: Drop current commands history and commands stack.
            self.setSourcePath(str(directory_uri))
            event.accept()
        else:
            event.ignore()
