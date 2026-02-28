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


class ImageCropService:
    """
    Crop the image.

    SHOULD be independent of any Commands and such. Just provide image uri and crop data and perform the crop.
    """

    def __init__(self):
        pass

    def crop(self, imageUri: str, cropRectangle: QRect):
        """
        Perform crop based on the given data.

        Backup original image
            Move original image into trash, so It can be recovered with Undo operation.
            Only original image is moved there.
            In case of multiple crops of the current image, original wont be overriden and therefore lost.

        :return:
        """
        # Prepare useful paths and names
        currentFilePath = pathlib.Path(imageUri)
        srcDir = currentFilePath.parent
        filename = currentFilePath.name

        print(f"Source dir: {srcDir}")
        print(f"Full path: {currentFilePath}")
        print(f"File name: {filename}")

        # Backup original (uncropped) file so Undo is possible
        trashDir = pathlib.Path(srcDir) / "__DELETED__"
        trashDir.mkdir(exist_ok=True)
        if not pathlib.Path(trashDir, filename).is_file():
            shutil.copy2(currentFilePath, pathlib.Path(trashDir, filename))

        # Load a pixmap and crop it
        pixmap = QPixmap(imageUri)

        # Crop original image and save update the preview
        croppedPixmap: QPixmap = pixmap.copy(cropRectangle)

        # Override original file with the cropped one in current directory
        croppedPixmap.save(imageUri)
