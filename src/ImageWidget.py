import logging
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
        
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.label)
        self.setMouseTracking(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        # self.layout.addWidget(self.rubberBand)
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
        scaledPixmapWidth = self.label.pixmap().rect().width()
        scaledPixmapHeight = self.label.pixmap().rect().height()
        labelWidth = self.label.rect().width()
        labelHeight = self.label.rect().height()

        xOff = (labelWidth - scaledPixmapWidth) / 2
        yOff = (labelHeight - scaledPixmapHeight) / 2
        return int(round(xOff)), int(round(yOff))

    def _transformPositionFromGlobalToPixmap(self, widgetCursorPosition: QPoint) -> QPoint:
        """

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


    def mousePressEvent(self, event):
        # TODO: move elsewhere???
        # TODO: V1: QRubberBand nebo V2: QGraphicView (okraje s kruhama v rozich a po stranach)

        # TODO: Fix: still small misalignment between cursor's tip position and rubberband.
        # TODO: Show rubberband to all directions, not just from top left to right down.
        self._dragging = True

        # Get cursor click position
        widgetCursorPosition: QPoint = event.pos()
        self._pixmapCursorStartPosition: QPoint = self._transformPositionFromGlobalToPixmap(widgetCursorPosition)
        log.info(f"[mousePressEvent] Pixmap start Position: {self._pixmapCursorStartPosition}")

        xOff, yOff = self._getPixmapCursorOffset()

        # Note: Geometry for the rubber band is different, than the pixmap's geometry.
        if not self.rubberBand:
            self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.label)
        self._startingRubberPoint = self._pixmapCursorStartPosition + QPoint(xOff, yOff)
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
            self._endingRubberPoint = self._pixmapCursorEndPosition + QPoint(xOff, yOff)

            if self._startingRubberPoint and self._endingRubberPoint:
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

        # TODO: save new crop into the list of changes, so we can undo change / completely revert all changes.
        croppedPixmap: QPixmap = self.pixmap.copy(cropAreaRect)
        self.pixmap.swap(croppedPixmap)
        self.updateScaledPixmap()

        # TODO: WIP: Save
        # TODO: Make UndoCrop() possible!!!!!
        # self.pixmap.save(self.currentImgPath)  # Override the image. WORKING! ... Dangerous !!! Must implement UndoCrop().
        self.pixmap.save(self.currentImgPath+"_cropped.png")  # Save with different name, keep original.

        # Clear variables and prepare for next cropping and rubberBand drawing
        self._pixmapCursorStartPosition = None
        self._pixmapCursorEndPosition = None

        self._startingRubberPoint = None
        self._endingRubberPoint = None

        self.rubberBand.hide()

        super().mouseReleaseEvent(event)
