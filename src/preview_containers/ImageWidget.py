import logging
import copy

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QRubberBand

from src.CropData import CropData
from src.GalleryItem import GalleryItem

log = logging.getLogger(__name__)


class ImageWidget(QWidget):

    """
    Class handling Images (png, jpeg and such) preview drawing and preparing for it.

    No other operations over Images should be there (like extracting text and so on)
    """

    requestImageCropSignal = pyqtSignal(CropData)

    def __init__(self):
        super().__init__()

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(False)

        self._imageData: GalleryItem = None
        self._pixmap = QPixmap()
        self.label.setPixmap(self._pixmap)

        # Coords for the image Crop
        self._pixmapCursorStartPosition = None
        self._pixmapCursorEndPosition = None

        # Coords for the rubberBand drawing
        self._startingRubberPoint = None
        self._endingRubberPoint = None

        self._dragging = False
        
        self.rubberBand = None
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)  # Needed for mouseMoveEvent to be called without pressing any button.

        self._showMouseGuideLines = True

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


    def updateImage(self, imageData: GalleryItem):
        # TODO: Use cache?
        self._imageData = imageData
        self._pixmap.load(imageData.pathAsStr())
        self.updateScaledPixmap()

    def resizeEvent(self, event):
        self.updateScaledPixmap()
        super().resizeEvent(event)

    def updateScaledPixmap(self):
        if self._pixmap:
            scaledPixmap = self._pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaledPixmap)

    # def getOriginalImageSize(self) -> QSize:
    #     if self.pixmap:
    #         return self.pixmap.size()
    #     return None

    @pyqtSlot(bool)
    def showMouseGuidelines(self, enabled: bool):
        self._showMouseGuideLines = enabled

    @staticmethod
    def clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n


    def _getPixmapCursorOffset(self):
        """
        # TODO: Tohle si myslim, ze by tez melo byt asi jinde...

        Returns the OFFSET of the pixmap's (0, 0) inside the label container.

        |<-----------label width------------>|
        |                  ^                 |
        |                  |                 |
        |                off_y               |
        |                  |                 |
        |                  v                 |
        |<---offsetX--->|~~~~|               |
        |               |~~~~|               |
        |               |~~~~|               |
        |               |____|               |
        |                                    |
        |                                    |
        |____________________________________|

        """

        scaledPixmapWidth = self.label.pixmap().rect().width()
        scaledPixmapHeight = self.label.pixmap().rect().height()
        labelWidth = self.label.rect().width()
        labelHeight = self.label.rect().height()

        xOff = (labelWidth - scaledPixmapWidth) / 2
        yOff = (labelHeight - scaledPixmapHeight) / 2

        # log.info("Pixmap Offset before round: ({}, {})".format(xOff, yOff))
        # log.info("Pixmap Offset after round: ({}, {})".format(round(xOff), round(yOff)))

        return int(round(xOff)), int(round(yOff))


    def _transformPositionFromGlobalToPixmap(self, widgetCursorPosition: QPoint) -> QPoint:
        """
        # TODO: Tohle si myslim, ze by tez melo byt asi jinde...
        # TODO: Zkusit event.globalPos(), screenPos(), localPos(). Mozna budu tyhle metody moct odstranit.
        """
        xOff, yOff = self._getPixmapCursorOffset()

        localPosition = widgetCursorPosition
        scaledPixmapCursorPositionX = localPosition.x() - xOff
        scaledPixmapCursorPositionY = localPosition.y() - yOff

        # print(f"Cursor Offset: {xOff}, {yOff}")
        # log.info(f"Click position mapped to the scaled pixmap: ({scaledPixmapCursorPositionX}, {scaledPixmapCursorPositionY})")

        # Check, that the clicking outside of pixmap does not have effect
        xw = ImageWidget.clamp(localPosition.x() - xOff, 0, scaledPixmapCursorPositionX)
        yw = ImageWidget.clamp(localPosition.y() - yOff, 0, scaledPixmapCursorPositionY)
        # log.info(f"Clamped: {xw}, {yw}")

        # return QPoint(int(round(scaledPixmapCursorPositionX)), int(round(scaledPixmapCursorPositionY)))
        return QPoint(int(round(xw)), int(round(yw)))


    def _transformPositionFromScaledPixmapToUnscaled(self, scaledPixmapCursorPosition: QPoint) -> QPoint:
        """
        # TODO: Tohle si myslim, ze by tez melo byt asi jinde..
        """
        # Gather facts about label area and current pixmap's area (both original and scaled)
        pixmapWidth = self._pixmap.rect().width()
        pixmapHeight = self._pixmap.rect().height()
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
        # print(f"InitialPos: {self._initialRubberClickPosition}")
        # print(f"StartingPos: {self._startingRubberPoint}")
        # print(f"current position: {currentCursorPosition}")
        # print(f"EndingPos: {self._endingRubberPoint}")

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


    def mousePressEvent(self, event):
        # TODO: move elsewhere??? Maybe into GalleryManager, because I want this to use also on Videos...
        # TODO: V1: QRubberBand nebo V2: QGraphicView (okraje s kruhama v rozich a po stranach)
        # TODO: A mouseEvent handling a rubberband drawing presunout do toho GalleryManager asi,

        self._dragging = True

        # Get cursor click position
        widgetCursorPosition: QPoint = event.pos()
        self._pixmapCursorStartPosition: QPoint = self._transformPositionFromGlobalToPixmap(widgetCursorPosition)
        log.info(f"[mousePressEvent] Pixmap start Position: {self._pixmapCursorStartPosition}")

        xOff, yOff = self._getPixmapCursorOffset()
        rubberBandDrawOffsetCompensation = QPoint(10, 10)  # Compensation for small misalignment between cursor tip and rubberband start.

        # Note: Geometry for the rubber band is different, than the pixmap's geometry.
        if not self.rubberBand:
            self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.label)
            self._initialRubberClickPosition = self._pixmapCursorStartPosition + QPoint(xOff, yOff) - rubberBandDrawOffsetCompensation
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
        super().mouseMoveEvent(event)

        if self._dragging:  # Prevents crash when just moving without initial click.
            currentPosition: QPoint = event.pos()
            self._pixmapCursorEndPosition: QPoint = self._transformPositionFromGlobalToPixmap(currentPosition)

            xOff, yOff = self._getPixmapCursorOffset()
            rubberBandDrawOffsetCompensation = QPoint(10, 10)  # Compensation for small misalignment between cursor tip and rubberband start.

            # RubberBand drawing
            currentTransformedCursorPosition = self._pixmapCursorEndPosition + QPoint(xOff, yOff) - rubberBandDrawOffsetCompensation
            # self._endingRubberPoint = currentTransformedCursorPosition

            if self._startingRubberPoint and self._endingRubberPoint:
                self.augmentStartAndEndRubberCoords(currentTransformedCursorPosition)
                self.rubberBand.setGeometry(QRect(self._startingRubberPoint, self._endingRubberPoint))
            else:
                log.warning(f"[mouseMoveEvent]: startPosition or endPosition not initialised!")
        
        # Draw cross line to indicate boundaries of the start of the crop area relative to cursor
        if self._showMouseGuideLines:
            pixmapCursorEndPosition: QPoint = self._transformPositionFromGlobalToPixmap(event.pos())
            px = self._pixmap.copy()
            scaledTmpPixmap = px.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter = QPainter(scaledTmpPixmap)
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawLine(pixmapCursorEndPosition.x()-10, 0, pixmapCursorEndPosition.x()-10, self.label.height())
            painter.drawLine(0, pixmapCursorEndPosition.y()-10, self.label.width(), pixmapCursorEndPosition.y()-10)
            painter.end()
            self.label.setPixmap(scaledTmpPixmap)
        
        # self.drawCropPreview(QRect(50, 50, 200, 270))


    def leaveEvent(self, a0):
        self.updateScaledPixmap()  # Draw original image back when cursor leaves the widget area.
        return super().leaveEvent(a0)


    def mouseReleaseEvent(self, event):
        self._dragging = False

        # Calculate final positions based on the rubberBand coords (not dependent on the drag direction)
        # The calculation takes into account the augmented start and end rubber coords, so all directions are handled.
        self._pixmapCursorStartPosition: QPoint = self._transformPositionFromGlobalToPixmap(self._startingRubberPoint)
        self._pixmapCursorEndPosition: QPoint = self._transformPositionFromGlobalToPixmap(self._endingRubberPoint)
        # log.info(f"[mouseReleaseEvent] Pixmap start Position: {self._pixmapCursorEndPosition}")

        # Crop original image and save
        unscaledStartPosition = self._transformPositionFromScaledPixmapToUnscaled(self._pixmapCursorStartPosition)
        unscaledEndPosition = self._transformPositionFromScaledPixmapToUnscaled(self._pixmapCursorEndPosition)
        cropAreaRect = QRect(unscaledStartPosition, unscaledEndPosition)
        
        # Prevent cropping to too small area
        if cropAreaRect.height() < 6 or cropAreaRect.width() < 6:
            log.warning("Crop area too small, cancelling cropping operation.")
            # Clear variables and prepare for next cropping and rubberBand drawing
            self._pixmapCursorStartPosition = None
            self._pixmapCursorEndPosition = None

            self._startingRubberPoint = None
            self._endingRubberPoint = None

            self.rubberBand.hide()
            self.rubberBand = None

            super().mouseReleaseEvent(event)
            return

        # Harvest crop data and send them for processing
        cropData = CropData(
            imageData=self._imageData,
            cropRectangle=cropAreaRect,
            originalImageSize=self._pixmap.size()
        )

        self.requestImageCropSignal.emit(cropData)
        log.info(f"Image Widget: CropData emitted: {cropData}")

        # Clean-up variables and prepare for next cropping and rubberBand drawing
        self._pixmapCursorStartPosition = None
        self._pixmapCursorEndPosition = None

        self._startingRubberPoint = None
        self._endingRubberPoint = None

        self.rubberBand.hide()
        self.rubberBand = None
        super().mouseReleaseEvent(event)


    # TODO: WIP: Does not work. Event is not registered. It is caught by SortModeHandler instead.
    def keyPressEvent(self, event):
        """
        Cancel the cropping when ESC key is pressed.
        """

        log.info(f"Key pressed: {event.key()}")
        if event.key() == Qt.Key_Escape:

            # Cancel current cropping operation
            self._dragging = False

            self._pixmapCursorStartPosition = None
            self._pixmapCursorEndPosition = None

            self._startingRubberPoint = None
            self._endingRubberPoint = None

            if self.rubberBand:
                self.rubberBand.hide()
                self.rubberBand = None

            log.info("Cropping operation cancelled.")
            return

        return super().keyPressEvent(event)
    

    def drawCropPreview(self, cropRect: QRect):
        """
        If enabled and any available, draws a preview of the possible crop operation result based on previous crop.
        
        TODO: WIP.
        """
        square = cropRect
        px = self._pixmap.copy()
        scaledTmpPixmap = px.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter = QPainter(scaledTmpPixmap)
        painter.setPen(QPen(Qt.red, 1))
        painter.drawRects(square)
        painter.end()
        self.label.setPixmap(scaledTmpPixmap)