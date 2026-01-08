import shutil
import os

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint

# TODO:
# from send2trash import send2trash
# send2trash(str(p))

class CropImageCommand(QUndoCommand):

    CMD_ID = 1001

    def __init__(self, image, imageSrcPath, cropRectangle, originalImageSize):
        super().__init__()
        self.imageName = image
        self.imageSrcPath = imageSrcPath
        self.cropRectangle: QRect = cropRectangle
        self.originalImageSize: QSize = originalImageSize
    

    def id(self) -> int:
        return self.CMD_ID


    def mergeWith(self, other) -> bool:
        if not isinstance(other, CropImageCommand):
            return False
        if self.imageSrcPath != other.imageSrcPath:
            return False

        # update stored state
        self.cropRectangle = QRect(other.cropRectangle)
        self.originalImageSize = QSize(other.originalImageSize)

        # Optional but often useful: make redo idempotent and re-apply:
        # self.redo()

        return True


    def execute(self):
        pass
        #self.image.crop(self.crop_rectangle)

    def undo(self):
        # 1. Check, that original image still exists in the __deleted__ directory
        # 2. Move it back to the source directory (override the cropped one)
        # 3. Pop this command from the command stack
        
        # TMP solution (no checks)
        # Remove cropped image
        os.remove(self.imageSrcPath + "/" + self.imageName)

        # Restore original image
        shutil.move(self.imageSrcPath + "/__DELETED__/" + self.imageName, self.imageSrcPath + "/" + self.imageName)
