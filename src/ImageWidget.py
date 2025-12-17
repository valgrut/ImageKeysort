import logging
import os
import pathlib
import shutil
import copy

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QRubberBand

log = logging.getLogger(__name__)


class ImageWidget(QWidget):

    """
    Class handling Images (png, jpeg and such) preview drawing and preparing for it.

    No other operations over Images should be there (like extracting text and so on)
    """

    def __init__(self):
        super().__init__()

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(False)

        self.currentImgPath = ""
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)

        # Coords for the image Crop
        self._pixmapCursorStartPosition = None
        self._pixmapCursorEndPosition = None

        # Coords for the rubberBand drawing
        self._startingRubberPoint = None
        self._endingRubberPoint = None

        self._dragging = False
        
        self.rubberBand = None #  QRubberBand(QRubberBand.Rectangle, self.label)
        self.setMouseTracking(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def updateImage(self, img_path):
        # TODO: Use cache?
        self.pixmap.load(img_path)
        self.currentImgPath = img_path
        self.updateScaledPixmap()

    def resizeEvent(self, event):
        self.updateScaledPixmap()
        super().resizeEvent(event)

    def updateScaledPixmap(self):
        if self.pixmap:
            scaledPixmap = self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaledPixmap)

    @staticmethod
    def clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n

    def _getPixmapCursorOffset(self):
        # TODO: Tohle si myslim, ze by tez melo byt asi jinde...
        scaledPixmapWidth = self.label.pixmap().rect().width()
        scaledPixmapHeight = self.label.pixmap().rect().height()
        labelWidth = self.label.rect().width()
        labelHeight = self.label.rect().height()

        xOff = (labelWidth - scaledPixmapWidth) / 2
        yOff = (labelHeight - scaledPixmapHeight) / 2
        return int(round(xOff)), int(round(yOff))

    def _transformPositionFromGlobalToPixmap(self, widgetCursorPosition: QPoint) -> QPoint:
        """
        # TODO: Tohle si myslim, ze by tez melo byt asi jinde...
        """
        xOff, yOff = self._getPixmapCursorOffset()

        localPosition = widgetCursorPosition
        scaledPixmapCursorPositionX = localPosition.x() - xOff
        scaledPixmapCursorPositionY = localPosition.y() - yOff

        # print(f"Cursor Offset: {xOff}, {yOff}")
        log.info(f"Click position mapped to the scaled pixmap: ({scaledPixmapCursorPositionX}, {scaledPixmapCursorPositionY})")

        # Check, that the clicking outside of pixmap does not have effect
        xw = ImageWidget.clamp(localPosition.x() - xOff, 0, scaledPixmapCursorPositionX)
        yw = ImageWidget.clamp(localPosition.y() - yOff, 0, scaledPixmapCursorPositionY)
        log.info(f"Clamped: {xw}, {yw}")

        # return QPoint(int(round(scaledPixmapCursorPositionX)), int(round(scaledPixmapCursorPositionY)))
        return QPoint(int(round(xw)), int(round(yw)))


    def _transformPositionFromScaledPixmapToUnscaled(self, scaledPixmapCursorPosition: QPoint) -> QPoint:
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


    def augmentStartAndEndRubberCoords(self, currentCursorPosition: QPoint = None):
        print(f"InitialPos: {self._initialRubberClickPosition}")
        print(f"StartingPos: {self._startingRubberPoint}")
        print(f"current position: {currentCursorPosition}")
        print(f"EndingPos: {self._endingRubberPoint}")

        # Cursor is moved to left from initial click
        if self._initialRubberClickPosition.x() > currentCursorPosition.x():
            self._startingRubberPoint.setX(currentCursorPosition.x())
            self._endingRubberPoint.setX(self._initialRubberClickPosition.x())

        # Cursor is moved to right from initial click
        if self._initialRubberClickPosition.x() <= currentCursorPosition.x():
            self._startingRubberPoint.setX(self._initialRubberClickPosition.x())
            self._endingRubberPoint.setX(currentCursorPosition.x())

        # Cursor is moved above from initial click
        if self._initialRubberClickPosition.y() > currentCursorPosition.y():
            self._startingRubberPoint.setY(currentCursorPosition.y())
            self._endingRubberPoint.setY(self._initialRubberClickPosition.y())
        
        # Cursor is moved below from initial click
        if self._initialRubberClickPosition.y() <= currentCursorPosition.y():
            self._startingRubberPoint.setY(self._initialRubberClickPosition.y())
            self._endingRubberPoint.setY(currentCursorPosition.y())

        # if self._startingRubberPoint and self._endingRubberPoint:
        #     starting = self._startingRubberPoint
        #     ending = self._endingRubberPoint

        #     self._startingRubberPoint.setX(min(starting.x(), ending.x()))
        #     self._startingRubberPoint.setY(min(starting.y(), ending.y()))
        #     self._endingRubberPoint.setX(max(starting.x(), ending.x()))
        #     self._endingRubberPoint.setY(max(starting.y(), ending.y()))


    def mousePressEvent(self, event):
        # TODO: move elsewhere??? Maybe into GalleryManager, because I want this to use also on Videos...
        # TODO: V1: QRubberBand nebo V2: QGraphicView (okraje s kruhama v rozich a po stranach)

        # TODO: Fix: still small misalignment between cursor's tip position and rubberband.
        # TODO: Show rubberband to all directions, not just from top left to right down.
        #   This will beed to swap start/end position dynamically based on the position of initial click and actual position before release.
        #   So, starting position will dynamically swap with current, if current is lesser than start.
        #   startx = min(startx, currentx)
        #   endx = max(startx, currentx)
        #   starty = min(starty, currenty)
        #   endy = max(starty, currenty)
        #   tento swap bude volany v mouseMoveEvent().
        #
        # TODO: Logika croppingu by mela byt separatni uplne pryc, jako TextExtraction.
        #
        # A mouseEvent handling a rubberband drawing presunout do toho GalleryManager asi,
        # abych to pak mohl pouzit i pro videa.

        self._dragging = True

        # Get cursor click position
        widgetCursorPosition: QPoint = event.pos()
        self._pixmapCursorStartPosition: QPoint = self._transformPositionFromGlobalToPixmap(widgetCursorPosition)
        log.info(f"[mousePressEvent] Pixmap start Position: {self._pixmapCursorStartPosition}")

        xOff, yOff = self._getPixmapCursorOffset()

        # Note: Geometry for the rubber band is different, than the pixmap's geometry.
        if not self.rubberBand:
            self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.label)
            self._initialRubberClickPosition = self._pixmapCursorStartPosition + QPoint(xOff, yOff)
            self._startingRubberPoint = copy.deepcopy(self._initialRubberClickPosition)
            self._endingRubberPoint = copy.deepcopy(self._initialRubberClickPosition)  # Init both start and end points
            self.rubberBand.setGeometry(QRect(self._startingRubberPoint, QSize(0, 0)))
            self.rubberBand.show()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Note: This is executed always when just hovering above image. No click is required.

        :param event:
        :return:
        """

        if self._dragging:  # Prevents crash when just moving without initial click.
            currentPosition: QPoint = event.pos()
            self._pixmapCursorEndPosition: QPoint = self._transformPositionFromGlobalToPixmap(currentPosition)

            xOff, yOff = self._getPixmapCursorOffset()

            # RubberBand drawing
            currentTransformedCursorPosition = self._pixmapCursorEndPosition + QPoint(xOff, yOff)
            # self._endingRubberPoint = currentTransformedCursorPosition

            if self._startingRubberPoint and self._endingRubberPoint:
                self.augmentStartAndEndRubberCoords(currentTransformedCursorPosition)
                self.rubberBand.setGeometry(QRect(self._startingRubberPoint, self._endingRubberPoint))
            else:
                log.warning(f"[mouseMoveEvent]: startPosition or endPosition not initialised!")

        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        self._dragging = False

        widgetTargetPosition: QPoint = event.pos()
        self._pixmapCursorEndPosition: QPoint = self._transformPositionFromGlobalToPixmap(widgetTargetPosition)
        log.info(f"[mouseReleaseEvent] Pixmap start Position: {self._pixmapCursorEndPosition}")

        # Crop original image and save
        unscaledStartPosition = self._transformPositionFromScaledPixmapToUnscaled(self._pixmapCursorStartPosition)
        unscaledEndPosition = self._transformPositionFromScaledPixmapToUnscaled(self._pixmapCursorEndPosition)
        cropAreaRect = QRect(unscaledStartPosition, unscaledEndPosition)


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

        # TODO: Check that QRect je podmnozina image.rect()
        # TODO: save new crop into the list of changes, so we can undo change / completely revert all changes.
        # TODO: Make UndoCrop() possible!!!!!

        # Crop original image and save update the preview
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


        # Clear variables and prepare for next cropping and rubberBand drawing
        self._pixmapCursorStartPosition = None
        self._pixmapCursorEndPosition = None

        self._startingRubberPoint = None
        self._endingRubberPoint = None

        self.rubberBand.hide()
        self.rubberBand = None

        super().mouseReleaseEvent(event)
