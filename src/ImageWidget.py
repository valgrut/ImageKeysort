import logging
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize
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

        # self.rubberBand = None
        # # self.setMouseTracking(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.rubberBand)
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
    #     # determine selection, for example using QRect.intersects()
    #     # and QRect.contains(
    #     rect = self.rubberBand.geometry()
    #     log.info(f"[mouseRelease] Selected area: {rect}")
    #     log.info(f"[mouseRelease] pixmap geometry: {self.pixmap.rect()}")
    #     log.info(f"[mouseRelease] label geometry: {self.label.rect()}")
    #     intersection = rect.intersects(self.pixmap.rect())
    #     log.info(f"[mouseRelease] Intersection: {intersection}")
    #     # self.mouseReleaseEvent(self, event)
    #
