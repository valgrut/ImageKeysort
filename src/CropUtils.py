import logging
import os
import pathlib
import shutil

import ffmpeg

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel


# TODO: priority: Make command Undo-able even in this WIP version.


log = logging.getLogger(__name__)


class CropUtils:
    
    @staticmethod
    def clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n


    @staticmethod
    def _getPixmapCursorOffset(pixmapLabel: QLabel):
        """
        pixmapLabel: QLabel containing the pixmap.
        """
        scaledPixmapWidth = pixmapLabel.pixmap().rect().width()
        scaledPixmapHeight = pixmapLabel.pixmap().rect().height()
        labelWidth = pixmapLabel.rect().width()
        labelHeight = pixmapLabel.rect().height()

        xOff = (labelWidth - scaledPixmapWidth) / 2
        yOff = (labelHeight - scaledPixmapHeight) / 2
        return int(round(xOff)), int(round(yOff))


    @staticmethod
    def _transformPositionFromGlobalToPixmap(widgetCursorPosition: QPoint) -> QPoint:
        """
        """
        xOff, yOff = CropUtils._getPixmapCursorOffset()

        localPosition = widgetCursorPosition
        scaledPixmapCursorPositionX = localPosition.x() - xOff
        scaledPixmapCursorPositionY = localPosition.y() - yOff

        # print(f"Cursor Offset: {xOff}, {yOff}")
        log.info(f"Click position mapped to the scaled pixmap: ({scaledPixmapCursorPositionX}, {scaledPixmapCursorPositionY})")

        # Check, that the clicking outside of pixmap does not have effect
        xw = CropUtils.clamp(localPosition.x() - xOff, 0, scaledPixmapCursorPositionX)
        yw = CropUtils.clamp(localPosition.y() - yOff, 0, scaledPixmapCursorPositionY)
        log.info(f"Clamped: {xw}, {yw}")

        # return QPoint(int(round(scaledPixmapCursorPositionX)), int(round(scaledPixmapCursorPositionY)))
        return QPoint(int(round(xw)), int(round(yw)))


    @staticmethod
    def _transformPositionFromScaledPixmapToUnscaled(scaledPixmapCursorPosition: QPoint) -> QPoint:
        """
        # TODO: Tohle si myslim, ze by tez melo byt asi jinde...
        """
        # Gather facts about label area and current pixmap's area (both original and scaled)
        pixmapWidth = self.pixmap.rect().width()
        pixmapHeight = self.pixmap.rect().height()
        scaledPixmapWidth = self.label.pixmap().rect().width()
        scaledPixmapHeight = self.label.pixmap().rect().height()

        # if scaledPixmapWidth == 0 or scaledPixmapHeight == 0:
        #     print("NULA!!!!!!")
        #     return None

        # Translate offset point into original unscaled image (so the original can be cropped then)
        scaleRatio = min(pixmapWidth / scaledPixmapWidth, pixmapHeight / scaledPixmapHeight)

        # log.info(f"Pixmap scale ratio: {scaleRatio}")
        pixmapCursorPositionX = scaledPixmapCursorPosition.x() * scaleRatio  # TODO: floor / ceiling
        pixmapCursorPositionY = scaledPixmapCursorPosition.y() * scaleRatio  # TODO: floor / ceiling
        # log.info(f"Click position mapped to the Unscaled pixmap: {pixmapCursorPositionX}, {pixmapCursorPositionY}")

        return QPoint(int(round(pixmapCursorPositionX)), int(round(pixmapCursorPositionY)))


    # def cropImage(self, imagePath, originalImageCropRect: QRect):
    #     """
    #     :param image: Path of the image to crop.
    #     :param originalImageCropRectangle: Coords of the rectanhle in the UNSCALED pixmap/image.
    #         The user selects area to be cropped via rubberband selection.
    #         The coords are transformed from the scaled coords into coords corresponding to the original size pixmap.
    #     :return:
    #     """

    #     # Prepare useful paths and names
    #     currentFilePath = pathlib.Path(self.currentImgPath)
    #     print(f"Full path: {currentFilePath}")
    #     currentFileNameNoExt = currentFilePath.stem
    #     print(f"File without ext: {currentFileNameNoExt}")
    #     currentSrcDirPath = currentFilePath.parent
    #     print(f"Source dir: {currentSrcDirPath}")
    #     extension = currentFilePath.suffix
    #     print(f"Extension: {extension}")
    #     currentFile = currentFilePath.name
    #     print(f"File name: {currentFile}")

    #     # Backup original image
    #     #   Move original image into trash, so It can be recovered with Undo operation.
    #     #   Only original image is moved there.
    #     #   In case of multiple crops of the current image, original wont be overriden and therefore lost.
    #     trashDir = pathlib.Path(currentSrcDirPath) / "__DELETED__"
    #     trashDir.mkdir(exist_ok=True)
    #     if not pathlib.Path(trashDir, currentFile).is_file():
    #         shutil.copy2(currentFilePath, pathlib.Path(trashDir, currentFile))

    #     # TODO: Use this function to crop, NOW it is directly in the ImageWidget ....
    #     # TODO: Check that QRect je podmnozina image.rect()
    #     # TODO: save new crop into the list of changes, so we can undo change / completely revert all changes.
    #     # TODO: Make UndoCrop() possible!!!!!

    #     # Crop original image and save update the preview
    #     cropAreaRect = originalImageCropRect
    #     croppedPixmap: QPixmap = self.pixmap.copy(cropAreaRect)
    #     self.pixmap.swap(croppedPixmap)
    #     self.updateScaledPixmap()

    #     # Perform crop
    #     # Variant 1 - create cropped image with different name than original
    #     # croppedFileName = pathlib.Path(currentSrcDirPath / (currentFileNameNoExt + "_cropped" + extension))
    #     # print(f"Cropped file name: {croppedFileName}")
    #     # self.pixmap.save(str(croppedFileName))  # Save with different name, keep original.

    #     # Variant 2 - Override original file with the cropped one
    #     self.pixmap.save(self.currentImgPath)  # Override the image. WORKING! ... Dangerous !!! Must implement UndoCrop().


    @staticmethod
    def cropVideo(self, videoPath, originalImageCropRect: QRect):
        # TODO (using ffmpeg)
        pass