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
        self.imageData: GalleryItem = imageData
        self.cropRectangle: QRect = cropRectangle
        self.originalImageSize: QSize = originalImageSize

    def id(self) -> int:
        return self.CMD_ID

    def mergeWith(self, otherCommand: QUndoCommand) -> bool:
        # TODO: Recalculate the crop rectangle of the cropped image to correspond to its original size, not the cropped one.
        #   (in case of recropping the same picture multiple times)
        # _globStartX = existingCommand.cropRectangle.height() + command.cropRectangle.height()
        # _globStartY = existingCommand.cropRectangle.width() + command.cropRectangle.width()
        # _globEndX = min(existingCommand.cropRectangle.width(), command.cropRectangle.width())
        # _globEndY = max(existingCommand.cropRectangle.height(), command.cropRectangle.height())
        # existingCommand.cropRectangle = QRect(QPoint(_globStartX, _globStartY), QPoint(_globEndX, _globEndY))

        print(f"CHECK: {self.cropRectangle} updated to {otherCommand.cropRectangle}")

        # update stored crop data
        self.cropRectangle = QRect(otherCommand.cropRectangle)
        self.originalImageSize = QSize(otherCommand.originalImageSize)

        return True

    def execute(self):
        print("Execute")
        cropService = ImageCropService()
        cropService.crop(self.imageData.pathAsStr(), self.cropRectangle)

    def undo(self):
        # 1. Check, that original image still exists in the __deleted__ directory
        # 2. Move it back to the source directory (override the cropped one)
        # 3. Pop this command from the command stack
        
        # TMP solution (no checks)
        # Remove cropped image
        os.remove(self.imageSrcPath + "/" + self.imageName)

        # Restore original image
        shutil.move(self.imageSrcPath + "/__DELETED__/" + self.imageName, self.imageSrcPath + "/" + self.imageName)
