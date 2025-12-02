import ffmpeg
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QWidget


class Cropper(QWidget):
    def __init__(self):
        super().__init__()


    def performCrop(self, image, originalImageCropRectangle):
        """
        :param image: Path of the image to crop.
        :param originalImageCropRectangle: Coords of the rectanhle in the UNSCALED pixmap/image.
            The user selects area to be cropped via rubberband selection.
            The coords are transformed from the scaled coords into coords corresponding to the original size pixmap.
        :return:
        """

        # Crop original image and save
        unscaledStartPosition = self._transformPositionFromScaledPixmapToUnscaled(self._pixmapCursorStartPosition)
        unscaledEndPosition = self._transformPositionFromScaledPixmapToUnscaled(self._pixmapCursorEndPosition)
        cropAreaRect = QRect(unscaledStartPosition, unscaledEndPosition)

        # TODO: save new crop into the list of changes, so we can undo change / completely revert all changes.
        croppedPixmap: QPixmap = self.pixmap.copy(cropAreaRect)
        self.pixmap.swap(croppedPixmap)
        self.updateScaledPixmap()

        # TODO: WIP: Save
        # TODO: Make UndoCrop() possible!!!!!
        # self.pixmap.save(self.currentImgPath)  # Override the image. WORKING! ... Dangerous !!! Must implement UndoCrop().
        self.pixmap.save(self.currentImgPath + "_cropped.png")  # Save with different name, keep original.
