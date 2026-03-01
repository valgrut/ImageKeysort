import logging
import pathlib
import shutil
import os

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint

from src.GalleryItem import GalleryItem
from src.file_operations.ImageRotateService import ImageRotateService

log = logging.getLogger(__name__)


class ImageRotateCommand(QUndoCommand):
    CMD_ID = 1002

    def __init__(self, imageData: GalleryItem):
        super().__init__()
        self._fileData: GalleryItem = imageData
        self.numberOfRotations: int = 0

    def id(self) -> int:
        return self.CMD_ID

    def mergeWith(self, otherCommand: QUndoCommand):
        """
        In case this image will be rotated multiple times, just merge the commands into one.
        # TODO: Finish this
        """
        # update stored crop data
        self.numberOfRotations += otherCommand.numberOfRotations

    def execute(self):
        ImageRotateService().rotate90(self._fileData.pathAsStr())
        self.numberOfRotations += 1
        print(f"{self.numberOfRotations}")

    def undo(self):
        # TODO:
        # 1. Check, that original image still exists in the __deleted__ directory
        # 2. Move it back to the source directory (override the cropped one)
        # 3. Pop this command from the command stack

        # TMP solution (no checks):
        # Remove cropped image
        os.remove(self._fileData.pathAsStr())

        # Restore original image
        deleteDirectory = str(self._fileData.sourcePath / pathlib.Path("__DELETED__") / pathlib.Path(self._fileData.fileName))
        shutil.move(deleteDirectory, self._fileData.pathAsStr())
