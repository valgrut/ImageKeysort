import pathlib
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

    def id(self) -> int:
        return self.CMD_ID

    def mergeWith(self, otherCommand: QUndoCommand):
        print(f"Original rectangle: {self.cropRectangle}")
        print(f"Second rectangle: {otherCommand.cropRectangle}")
        
        # TODO: Recalculate the crop rectangle of the cropped image to correspond to its original size, not the cropped one.
        #   (in case of recropping the same picture multiple times)
        # _globStartX = self.cropRectangle.x() + otherCommand.cropRectangle.x()
        # _globStartY = self.cropRectangle.y() + otherCommand.cropRectangle.y()
        # # _globEndX = min(self.cropRectangle.x(), otherCommand.cropRectangle.x())
        # # _globEndY = max(self.cropRectangle.y(), otherCommand.cropRectangle.y())
        # _globEndX = self.cropRectangle.width() - otherCommand.cropRectangle.width()
        # _globEndY = self.cropRectangle.height() - otherCommand.cropRectangle.height()
        # self.cropRectangle = QRect(QPoint(_globStartX, _globStartY), QPoint(_globEndX, _globEndY))

        # print(f"CHECK: {self.cropRectangle} updated to {otherCommand.cropRectangle}")

        # update stored crop data
        self.cropRectangle = QRect(otherCommand.cropRectangle)
        # self.originalImageSize = QSize(otherCommand.originalImageSize)


    def execute(self):
        ImageCropService().crop(self._fileData.pathAsStr(), self.cropRectangle)

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
