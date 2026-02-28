import pathlib
from os import listdir
from os.path import isfile, join
from pathlib import Path
import logging

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QMimeDatabase
from PyQt5.QtWidgets import QFileDialog, QGraphicsDropShadowEffect, QStackedWidget

from src.preview_containers.EmptyGalleryWidget import EmptyGalleryImageWidget
from src.MediaContainerWidget import MediaContainerWidget
from src.CropData import CropData
# from Gallery import Gallery
from src.GalleryItem import GalleryItem

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
    requestImageCropSignal = pyqtSignal(CropData)
    setEnabledCursorGuidelinesSignal = pyqtSignal(bool)

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
        self._sourceDirectoryPath: pathlib.Path = None
        self._availableMediaFiles: list[GalleryItem] = []
        self._currentFileIndex: int = -1  # Index with a value -1 represents empty gallery.

        # TODO: Future feature (multiple opened tabs representing separated galleries (source directories). vvvvv
        # self._galleryIndex = -1  # No gallery is currently available (loaded)
        # self._galleries: list[Gallery] = []
        # ^^^^^

        #self.allowedSuffixes = ('.png', '.jpg', '.jpeg', '.webp')
        self.textSuffixes = (".txt", ".log", ".csv", ".ini", ".json", ".xml", ".md", ".yaml", ".yml", ".py", ".cpp", ".c", ".h", ".html", ".htm", ".css", ".js")  # TODO: presunout do Settings a pridat dalsi text formaty (nebo to udelat nejak genericky)
        self.videoSuffixes = ("gif", "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm")  # TODO: presunout do Settings; spravit avi, zprovoznit mp4.
        self.allowedSuffixes = ('.png', '.jpg', '.jpeg', '.webp') + self.videoSuffixes + self.textSuffixes # TODO: presunout do Settings; spravit avi, zprovoznit mp4.

        # Stacked widgets:
        self.emptyInboxWidget = EmptyGalleryImageWidget()
        self.mediaContainerWidget = MediaContainerWidget(self)

        self.EMPTY_INBOX_WIDGET = 0
        self.MEDIA_WIDGET = 1

        self.addWidget(self.emptyInboxWidget)
        self.addWidget(self.mediaContainerWidget)

        self.setCurrentIndex(self.EMPTY_INBOX_WIDGET)
        # log.info(f"[INIT] mediaContainerWidget: {id(self.mediaContainerWidget)}")

        self.mediaContainerWidget.requestImageCropSignal.connect(self.requestImageCropSignal)  # Re-emit signal
        self.mainWindow.updateMediaPreviewSignal.connect(self.updatePreview)
        # self.rotateImageSignal.connect(self.mediaContainerWidget.rotateImageSignal)
        self.mainWindow.setEnabledCursorGuidelinesSignal.connect(self.setEnabledCursorGuidelinesSignal)


    # TODO: future feature.
    # def getActiveGallery(self):
    #     if self._galleryIndex >= 0:
    #         return self._galleries[self._galleryIndex]
    #     return None

    def setSourcePath(self, source_path: pathlib.Path | str):
        # TODO: future feature.
        # activeGallery = self.getActiveGallery()
        # if activeGallery is None:
        #     return

        if isinstance(source_path, str):
            resultPath = pathlib.Path(source_path)
        if isinstance(source_path, pathlib.Path):
            resultPath = source_path

        self._sourceDirectoryPath = resultPath
        self.mediaContainerWidget.setSourceDirLabelText(str(resultPath))
        self.loadImagesInDirectory()

    def getSourcePath(self) -> pathlib.Path:
        return self._sourceDirectoryPath

    def selectSourceDirectory(self):
        srcPath = QFileDialog.getExistingDirectory(self.mainWindow, "Select source directory")
        if not srcPath:
            return

        self._sourceDirectoryPath = pathlib.Path(srcPath)
        self.mediaContainerWidget.setSourceDirLabelText(str(self._sourceDirectoryPath))
        self.loadImagesInDirectory()

    def loadImagesInDirectory(self):
        if not self._sourceDirectoryPath:
            log.info("DEBUG: Error, src dir path is empty")
            return

        self._availableMediaFiles.clear()
        # self.images = [f for f in listdir(self.sourceDirectoryPath) if isfile(join(self.sourceDirectoryPath, f))]
        # TODO: Refactor this to only include allowed file types based on enabled types in Settings.

        for mediaItem in listdir(self._sourceDirectoryPath):
            # Skip directories and such
            if not isfile(join(self._sourceDirectoryPath, mediaItem)):
                continue

            # Skip files with undesired suffix and which are not text files (by its content)
            if not mediaItem.lower().endswith(self.allowedSuffixes) and not self.isCurrentTextFile(join(self._sourceDirectoryPath, mediaItem)):
                continue

            # Populate a gallery list with the allowed files
            newGalleryItem = GalleryItem(fileName=mediaItem, sourcePath=self._sourceDirectoryPath)
            self._availableMediaFiles.append(newGalleryItem)

        self._availableMediaFiles.sort()
        self._currentFileIndex = 0
        self.updatePreview()  # TODO

    def isGalleryEmpty(self):
        """
        returns true if there is no media files in the gallery.
        """
        if not self._availableMediaFiles:
            return True
        return False

    def getGalleryIndex(self):
        return self._currentFileIndex

    def incrementGalleryIndex(self):
        if self._currentFileIndex < len(self._availableMediaFiles) -1:
            self._currentFileIndex += 1
        # log.info(f"DBG: new gallery_index: {self._currentFileIndex} out of {len(self.availableMediaFiles) - 1}")

    def decrementGalleryIndex(self):
        if self._currentFileIndex >= 1:
            self._currentFileIndex -= 1
        # log.info(f"DBG: new gallery_index: {self._currentFileIndex} out of {len(self.availableMediaFiles) - 1}")


    def isCurrentTextFile(self, path=None) -> bool:
        """
        returns true if current file is .txt or other text format
        """

        db = QMimeDatabase()
        if path is None:
            path = str(self._sourceDirectoryPath / Path(self.getCurrentFilename()))

        # 1) by filename (fast; catches Makefile, Dockerfile, etc. on many systems)
        # mt = db.mimeTypeForFile(path, QMimeDatabase.MatchExtension)
        # if mt.name().startswith("text/"):
        #     return True

        # 2) by content (slower; best for “no suffix” or wrong suffix)
        mt = db.mimeTypeForFile(path, QMimeDatabase.MatchContent)
        currentFilename = self.getCurrentFilename()
        if mt.name().startswith("text/"):
            log.info(f"Preview file: {currentFilename} of the type: {QMimeDatabase().mimeTypeForFile(currentFilename).name()}")
            return True

        # sometimes scripts/configs come as application/x-... but are still text
        if mt.inherits("text/plain"):
            log.info(f"Preview file: {currentFilename} of the type: {QMimeDatabase().mimeTypeForFile(currentFilename).name()}")
            return True

        return False

    def isCurrentVideo(self) -> bool:
        """
        returns true if current file (given by self._currentFileIndex) is a video.
        """

        if str(self._availableMediaFiles[self._currentFileIndex].fileName).endswith(self.videoSuffixes):
            return True
        return False

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
        self._currentFileIndex = 0
        self.updatePreview()  # TODO: sig-slots ?

    @pyqtSlot()
    def setLastImage(self):
        self._currentFileIndex = len(self._availableMediaFiles) - 1
        self.updatePreview()  # TODO: sig-slots ?

    def getCurrentGalleryItem(self) -> None | GalleryItem:
        """
        Returns gallery item (picture/text/video/...) object given by the index.
        :return: GalleryItem on given index
        """
        if self.isGalleryEmpty():
            return None

        return self._availableMediaFiles[self._currentFileIndex]

    def getCurrentFilename(self) -> str:
        """
        Returns just the string representation of the current file without its path.
        :return: current file's filename
        """
        if self.isGalleryEmpty():
            # raise Exception("Gallery is empty.")
            return ""

        return self.getCurrentGalleryItem().fileName

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

        # Common operations for all types of file
        currentFile = self.getCurrentGalleryItem()

        self.setCurrentWidget(self.mediaContainerWidget)

        # TODO: Refactor - prakticky se vsechny 3 opakuji, jen prvne nastavim VideoWidget, pak TextWidget...
        # Specific operations by the file type
        if self.isCurrentVideo():
            self.mediaContainerWidget.setVideoWidget()
            self.mediaContainerWidget.updateVideo(currentFile)  # Mozna spis prejmenovat na showVideo()
            self.disableExtractTextButtonSignal.emit()
            self.enableCropButtonSignal.emit()

        elif self.isCurrentTextFile():
            self.mediaContainerWidget.setTextWidget()
            self.mediaContainerWidget.updateTextFile(currentFile)
            self.disableExtractTextButtonSignal.emit()
            self.disableCropButtonSignal.emit()

        else:
            # It is image
            self.mediaContainerWidget.setImageWidget()
            self.mediaContainerWidget.updatePreviewImage(currentFile)  # Mozna spis prejmenovat na showImage()
            self.enableExtractTextButtonSignal.emit()
            self.enableCropButtonSignal.emit()

        self.updateFilenameLabelText()  # TODO: sig-slots
        self.updateCounterLabelText()  # TODO: sig-slots

        # Set focus to back to Gallery Manager so after adding shortcut, arrows still can be used to show next/previous image.
        self.setFocus()

    def getCounterString(self) -> str:
        counter: str = str(self._currentFileIndex + 1) + "/" + str(len(self._availableMediaFiles))
        return counter

    # TODO: Update to ImgDataObj version:
    # TODO: 1. Deleting of entry z availableMediaFiles se bude jen presouvat do deletedMediaFiles
    # TODO: 2. Undo move to presune zase zpet (nechci ztratit reference na dany GalleryItem v Commands)
    # TODO: tento addFile vrati soubor z deletedMediaFiles zpet do _availableMediaFiles.
    # TODO: _deletedMediaFiles pak budou dropnuty, kdyz se zmeni galerie a pod...
    def addFile(self, fileName: str, positionIndex:int=0):
        self._availableMediaFiles.insert(positionIndex, GalleryItem(fileName, self.getSourcePath()))

    @pyqtSlot()
    def renameFile(self):
        """
        Starts the filename edit process.
        """
        self.setFilenameTextEditSignal.emit()
        self.mediaContainerWidget.startFilenameEdit()

    # @pyqtSlot()
    # def rotateImageRight(self):
    #     """
    #     Rotates the current image 90 degrees to the right.
    #     TODO: Maybe move Rotate method here from MainWindow.
    #     """
    #     print("rotateImageRight called")
    #     # self.rotateImageSignal.emit()
    #     self.mediaContainerWidget.rotateImageSignal.emit()
    #     self.updatePreview()

    
    def commitNewFileName(self, newFileName):
        """
        Commits the new filename to the gallery's availableMediaFiles list.
        """
        currentGalleryItem = self.getCurrentGalleryItem()

        originalFilename = self.getCurrentFilename()

        originalFullPath = currentGalleryItem.pathAsPath()
        newFullPath = self.getSourcePath() / Path(newFileName)

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
            currentGalleryItem.fileName = newFileName
            originalFullPath.rename(newFullPath)
            self.updateFilenameLabelText()
            self.updateStatusBarLabelSignal.emit("File was renamed successfully.")
            log.info("File was renamed successfully.")


    def appendTagToName(self, tag: str = None):
        # TODO: Refactor this into FileTagger class.
        # TODO: Refactor this out - HIGH PRIORITY!!!

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
        isFound = False
        for file in self._availableMediaFiles:
            if file.fileName == fileName:
                self._availableMediaFiles.remove(file)
                isFound = True
                break

        if not isFound:
            return

        if self._currentFileIndex >= len(self._availableMediaFiles):
            self._currentFileIndex = len(self._availableMediaFiles) - 1


    def dragEnterEvent(self, event) -> None:
        """
        Enables drag and drop of directory from the outside of an app and set it as source directory.

        Multiple directories are opened as multiple tabs.
        """
        if event.mimeData().hasUrls:
            event.accept()
            # log.info(f"Drag enter: Has URL")
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        """
        Enables drag and drop of directory from the outside of an app and set it as source directory.

        Multiple directories are opened as multiple tabs.
        """
        if event.mimeData().hasUrls:
            event.accept()
            # log.info(f"Drag Move: Has URL")
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        """
        Enables drag and drop of directory from the outside of an app and set it as source directory.

        Multiple directories are opened as multiple tabs.
        """
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
