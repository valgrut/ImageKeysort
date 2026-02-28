import logging
import pathlib
import shutil

from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import QPixmap, QTransform

log = logging.getLogger(__name__)


class ImageRotateService:
    """
    Rotate the image.

    SHOULD be independent of any Commands and such. Just provide image uri and perform the rotation.
    """

    @staticmethod
    def rotate90(imageUri: str):
        """
        Rotates provided image 90 degrees to the right (clockwise).
        """
        # Prepare useful paths and names
        currentFilePath = pathlib.Path(imageUri)
        srcDir = currentFilePath.parent
        filename = currentFilePath.name

        print(f"Source dir: {srcDir}")
        print(f"Full path: {currentFilePath}")
        print(f"File name: {filename}")

        # Backup original (unrotated) file so Undo is possible.
        # If the file is already in the trash directory (from previous modifying operation like Crop), skip this.
        trashDir = pathlib.Path(srcDir) / "__DELETED__"
        trashDir.mkdir(exist_ok=True)
        if not pathlib.Path(trashDir, filename).is_file():
            shutil.copy2(currentFilePath, pathlib.Path(trashDir, filename))

        # Load a pixmap and crop it
        pixmap = QPixmap(imageUri)

        # Crop original image and save update the preview
        rotatedPixmap: QPixmap = pixmap.transformed(QTransform().rotate(90))

        # Override original file with the cropped one in current directory
        rotatedPixmap.save(imageUri)

        print("Pixmap rotation finished.")
        log.info("Pixmap rotation finished.")
