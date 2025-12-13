import os
import pathlib
import shutil

import ffmpeg

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget


# TODO: priority: Make command Undo-able even in this WIP version.


class Cropper(QWidget):
    def __init__(self, galleryManager):
        super().__init__()
        self.galleryManager = galleryManager


    def cropImage(self, imagePath, originalImageCropRect: QRect):
        """
        :param image: Path of the image to crop.
        :param originalImageCropRectangle: Coords of the rectanhle in the UNSCALED pixmap/image.
            The user selects area to be cropped via rubberband selection.
            The coords are transformed from the scaled coords into coords corresponding to the original size pixmap.
        :return:
        """

        # Prepare useful paths and names
        currentFilePath = pathlib.Path(self.currentImgPath)
        print(f"Full path: {currentFilePath}")
        currentFileNameNoExt = currentFilePath.stem
        print(f"File without ext: {currentFileNameNoExt}")
        currentSrcDirPath = currentFilePath.parent
        print(f"Source dir: {currentSrcDirPath}")
        extension = currentFilePath.suffix
        print(f"Extension: {extension}")
        currentFile = currentFilePath.name
        print(f"File name: {currentFile}")

        # Backup original image
        #   Move original image into trash, so It can be recovered with Undo operation.
        #   Only original image is moved there.
        #   In case of multiple crops of the current image, original wont be overriden and therefore lost.
        trashDir = pathlib.Path(currentSrcDirPath) / "__DELETED__"
        trashDir.mkdir(exist_ok=True)
        if not pathlib.Path(trashDir, currentFile).is_file():
            shutil.copy2(currentFilePath, pathlib.Path(trashDir, currentFile))

        # TODO: Use this function to crop, NOW it is directly in the ImageWidget ....
        # TODO: Check that QRect je podmnozina image.rect()
        # TODO: save new crop into the list of changes, so we can undo change / completely revert all changes.
        # TODO: Make UndoCrop() possible!!!!!

        # Crop original image and save update the preview
        cropAreaRect = originalImageCropRect
        croppedPixmap: QPixmap = self.pixmap.copy(cropAreaRect)
        self.pixmap.swap(croppedPixmap)
        self.updateScaledPixmap()

        # Perform crop
        # Variant 1 - create cropped image with different name than original
        # croppedFileName = pathlib.Path(currentSrcDirPath / (currentFileNameNoExt + "_cropped" + extension))
        # print(f"Cropped file name: {croppedFileName}")
        # self.pixmap.save(str(croppedFileName))  # Save with different name, keep original.

        # Variant 2 - Override original file with the cropped one
        self.pixmap.save(self.currentImgPath)  # Override the image. WORKING! ... Dangerous !!! Must implement UndoCrop().

    def cropVideo(self, videoPath, originalImageCropRect: QRect):
        # TODO (using ffmpeg)
        pass