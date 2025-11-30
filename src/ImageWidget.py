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

        self._pixmapCursorStartPosition = None
        self._pixmapCursorEndPosition = None
        # self.rubberBand = None
        # # self.setMouseTracking(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        # self.layout.addWidget(self.rubberBand)
        self.setLayout(self.layout)

    def updateImage(self, img_path):
        # TODO: Use cache?
        self.pixmap.load(img_path)
        self.currentImgPath = img_path
        self.updateScaledPixmap()

    # def resizeEvent(self, QKeyEvent: event):
    def resizeEvent(self, event):
        self.updateScaledPixmap()
        super().resizeEvent(event)

    def updateScaledPixmap(self):
        if self.pixmap:
            scaledPixmap = self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaledPixmap)

    # @staticmethod
    # def clamp(n, min, max):
    #     if n < min:
    #         return min
    #     elif n > max:
    #         return max
    #     else:
    #         return n

    def _transformPositionFromGlobalToPixmap(self, widgetCursorPosition: QPoint) -> QPoint:
        """

        """
        # Gather facts about label area and current pixmap's area (both original and scaled)
        scaledPixmapWidth = self.label.pixmap().rect().width()
        scaledPixmapHeight = self.label.pixmap().rect().height()
        labelWidth = self.label.rect().width()
        labelHeight = self.label.rect().height()

        # The incoming point is expected to be in label-local coordinates (event.pos() from the
        # label). If a different coordinate space is passed, callers should map it to the label
        # before calling this function.
        localPosition = widgetCursorPosition
        xOff = (labelWidth - scaledPixmapWidth) / 2
        yOff = (labelHeight - scaledPixmapHeight) / 2
        scaledPixmapCursorPositionX = localPosition.x() - xOff
        scaledPixmapCursorPositionY = localPosition.y() - yOff
        # print(f"Cursor Offset: {xOff}, {yOff}")
        # print(f"Click position mapped to the scaled pixmap: ({scaledPixmapCursorPositionX}, {scaledPixmapCursorPositionY})")

        # Check, that the clicking outside of pixmap does not have effect
        # TODO - finish clamp()
        # xw = ImageWidget.clamp(origin.x() - xOff, xOff, scaledPixmapWidth)
        # yw = ImageWidget.clamp(origin.y() - yOff, yOff, scaledPixmapHeight)
        # print(xw, yw)

        return QPoint(int(round(scaledPixmapCursorPositionX)), int(round(scaledPixmapCursorPositionY)))


    def _transformPositionFromScaledPixmapToUnscaled(self, scaledPixmapCursorPosition: QPoint) -> QPoint:
        """

        """
        # Gather facts about label area and current pixmap's area (both original and scaled)
        pixmapWidth = self.pixmap.rect().width()
        pixmapHeight = self.pixmap.rect().height()
        scaledPixmapWidth = self.label.pixmap().rect().width()
        scaledPixmapHeight = self.label.pixmap().rect().height()

        # Translate offset point into original unscaled image (so the original can be cropped then)
        scaleRatio = min(pixmapWidth / scaledPixmapWidth, pixmapHeight / scaledPixmapHeight)
        # log.info(f"Pixmap scale ratio: {scaleRatio}")
        pixmapCursorPositionX = scaledPixmapCursorPosition.x() * scaleRatio  # TODO: floor / ceiling
        pixmapCursorPositionY = scaledPixmapCursorPosition.y() * scaleRatio  # TODO: floor / ceiling
        # log.info(f"Click position mapped to the Unscaled pixmap: {pixmapCursorPositionX}, {pixmapCursorPositionY}")

        return QPoint(int(round(pixmapCursorPositionX)), int(round(pixmapCursorPositionY)))


    def mousePressEvent(self, event):
        # TODO: move elsewhere???
        # TODO: QRubberBand nebo QGraphicView (okraje s kruhama v rozich a po stranach)

        # Get cursor click position
        widgetCursorPosition: QPoint = event.pos()
        self._pixmapCursorStartPosition: QPoint = self._transformPositionFromGlobalToPixmap(widgetCursorPosition)
        log.info(f"[mousePressEvent] Pixmap start Position: {self._pixmapCursorStartPosition}")


    def mouseMoveEvent(self, event):
        currentPosition: QPoint = event.pos()
        self._pixmapCursorEndPosition: QPoint = self._transformPositionFromGlobalToPixmap(currentPosition)


    def mouseReleaseEvent(self, event):
        widgetTargetPosition: QPoint = event.pos()
        self._pixmapCursorEndPosition: QPoint = self._transformPositionFromGlobalToPixmap(widgetTargetPosition)

        # Crop original image and save
        unscaledStartPosition = self._transformPositionFromScaledPixmapToUnscaled(self._pixmapCursorStartPosition)
        unscaledEndPosition = self._transformPositionFromScaledPixmapToUnscaled(self._pixmapCursorEndPosition)
        cropAreaRect = QRect(unscaledStartPosition, unscaledEndPosition)
        croppedPixmap: QPixmap = self.pixmap.copy(cropAreaRect)
        log.info(f"[mouseReleaseEvent] Pixmap start Position: {self._pixmapCursorEndPosition}")
        self.pixmap.swap(croppedPixmap)
        self.updateScaledPixmap()

        self._pixmapCursorStartPosition = None
        self._pixmapCursorEndPosition = None



    # def mousePressEvent(self, event):
    #     origin = event.pos()
    #     log.info(f"[mousePressed] Origin position: {origin}")
    #     if not self.rubberBand:
    #         self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
    #     self.rubberBand.setGeometry(QRect(origin, origin))
    #     self.rubberBand.setStyleSheet("border: 1px solid black;")
    #     self.rubberBand.show()
    #     # self.mousePressEvent(self, event)
    #
    # def mouseMoveEvent(self, event):
    #     origin = event.pos()
    #     log.info(f"[mouseMove] Origin position: {origin}")
    #     self.rubberBand.setGeometry(QRect(origin, event.pos()).normalized())
    #     # self.rubberBand.update()
    #     # self.mouseMoveEvent(self, event)
    #
    # def mouseReleaseEvent(self, event):
    #     origin = event.pos()
    #     log.info(f"[mouseRelease] Origin position: {origin}")
    #     #self.rubberBand.hide()
    #     rect = self.rubberBand.geometry()
    #     log.info(f"[mouseRelease] Selected area: {rect}")
    #     log.info(f"[mouseRelease] pixmap geometry: {self.pixmap.rect()}")
    #     log.info(f"[mouseRelease] label geometry: {self.label.rect()}")
    #     intersection = rect.intersects(self.pixmap.rect())
    #     log.info(f"[mouseRelease] Intersection: {intersection}")
    #     # self.mouseReleaseEvent(self, event)
    #
