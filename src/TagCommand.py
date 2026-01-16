import shutil
import os

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint

# TODO: Rozhodnuti
# - Co delat v pripade rucni zmeny nazvu souboru? Zmenit basename pak i v odpovidajicim TagCommandu pro dany filename?

class TagCommand(QUndoCommand):

    CMD_ID = 1002

    def __init__(self, imagename, imageSrcPath, tag):
        super().__init__()
        self.imageName = imagename
        self.imageSrcPath = imageSrcPath
        self._addedTag = None
        self._originalFilename = ""
    

    def id(self) -> int:
        return self.CMD_ID


    def mergeWith(self, other) -> bool:
        if not isinstance(other, TagCommand):
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
        # Remove tag T from image file name
        if self._addedTag in self.imageName:
            self.imageName.replace(" " + self._addedTag, '')

        # TODO: Change filename in the list of images in the GalleryManager
        # TODO: Change the name of the file itself.
