from pathlib import Path
import shutil
import os

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint

from src.GalleryItem import GalleryItem
from src.file_operations.ImageCropService import ImageCropService

# TODO - utilize computer's trash instead of custom __delete__ directory:
# from send2trash import send2trash
# send2trash(str(p))


class CropImageCommand(QUndoCommand):

    CMD_ID = 1001

    def __init__(self, imageData: GalleryItem, cropRectangle: QRect, originalImageSize: QSize):
        super().__init__()
        self._fileData: GalleryItem = imageData
        self.cropRectangle: QRect = cropRectangle
        self.originalImageSize: QSize = originalImageSize
        self.absoluteCropRectangle: QRect = cropRectangle  # Calculated to relate to original uncropped image. For reusing data on next image.

    def id(self) -> int:
        return self.CMD_ID

    def mergeWith(self, otherCommand: QUndoCommand):
        """
        NOTE: Rekalkulace je nutna pro REPEAT CROP na dalsim obrazku. Ne pro additional crop of current image.
        Note: Musel bych prvne provest exec, a az pak rekalkulaci.
        Note: Protoze kdyz recroppuju 1 image vicekrat, tak ziskany Rect je relativni k jiz predtim croppnutemu obrazku.
        Note: Na rekalkulaci ale potrebuju QRect z tohoto i toho druheho commandu.
        """

        # Recalculate the crop rectangle of the cropped image to correspond to its original size, not the cropped one.
        # This allows to reuse those data and crop other image of the same size with the same crop data.
        _globStartX = self.absoluteCropRectangle.x() + otherCommand.cropRectangle.x()
        _globStartY = self.absoluteCropRectangle.y() + otherCommand.cropRectangle.y()

        _globEndX = otherCommand.cropRectangle.width()
        _globEndY = otherCommand.cropRectangle.height()

        # Note: Beware the QRect constructor. It gave negative values when provided (QPoint(), QPoint()).
        self.absoluteCropRectangle = QRect(_globStartX, _globStartY, _globEndX, _globEndY)

        # update stored crop data
        self.cropRectangle = QRect(otherCommand.cropRectangle)


    def execute(self):
        ImageCropService().crop(self._fileData.pathAsStr(), self.cropRectangle)

    def undo(self):
        # Remove cropped image
        os.remove(self._fileData.pathAsStr())  # TODO: Is this required? Couldn't I just override it by shutil.move?

        # Restore original image
        deleteDirectoryPath = self._fileData.sourcePath / Path("__DELETED__") / Path(self._fileData.fileName)
        if not deleteDirectoryPath.exists():
            print("Cannot undo crop. Original image (backup) was removed from __DELETED__.")
            return

        shutil.move(str(deleteDirectoryPath), self._fileData.pathAsStr())
