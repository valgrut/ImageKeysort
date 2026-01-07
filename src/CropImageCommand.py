from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint



class CropImageCommand(QUndoCommand):
    def __init__(self, image, imageSrcPath, cropRectangle):
        super().__init__()
        self.imageName = image
        self.imageSrcPath = imageSrcPath
        self.cropRectangle: QRect = cropRectangle
        

    def execute(self):
        self.image.crop(self.crop_rectangle)

    def undo(self):
        pass