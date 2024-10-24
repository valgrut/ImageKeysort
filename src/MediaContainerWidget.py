from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QStackedWidget, QLabel, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, \
    QVBoxLayout

from ImageWidget import ImageWidget
from VideoWidget import VideoWidget
from Styles import Styles


class MediaContainerWidget(QWidget):
    def __init__(self, galleryManager):
        super().__init__()
        self.galleryManager = galleryManager

        self.imageViewWidget = ImageWidget()  # for .png, .jpg, ...
        self.videoViewWidget = VideoWidget()  # for .gif and such
        self.stackedMediaWidget = QStackedWidget()

        self.stackedMediaWidget.addWidget(self.imageViewWidget)
        self.stackedMediaWidget.addWidget(self.videoViewWidget)

        right_layout = QVBoxLayout()

        self.source_dir_label = QLabel("Not selected")
        self.source_dir_label.setMaximumHeight(30)
        self.source_dir_label.setStyleSheet(f"""
            QLabel {{
                min-height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                background-color: {Styles.widgetsBgColor};
                font-weight: bold;
                font-size: 15px;
                xxmargin: 5px;
                }}
            """)
        right_layout.addWidget(self.source_dir_label)

        self.image_filename_label = QLabel()
        self.image_filename_label.setMaximumHeight(30)
        self.image_filename_label.setStyleSheet(f"""
            QLabel {{
                _min-height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                background-color: {Styles.widgetsBgColor};
                font-weight: bold;
                font-size: 15px;
                xxmargin: 5px;
                }}
            """)

        right_layout.addWidget(self.image_filename_label)
        right_layout.addWidget(self.stackedMediaWidget)

        previousshadowEffect = QGraphicsDropShadowEffect()
        previousshadowEffect.setOffset(3, 3)
        previousshadowEffect.setBlurRadius(10)
        self.previous_image_button = QPushButton("&Previous", self)
        self.previous_image_button.clicked.connect(self.showPreviousImage)
        self.previous_image_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.previous_image_button.setFocus(True)
        self.previous_image_button.setGraphicsEffect(previousshadowEffect)
        self.previous_image_button.setStyleSheet(f"""
        QPushButton {{
            width: 150px;
            height: 20px;
            border: 1px solid black;
            border-radius: {Styles.buttonBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
            font-weight: bold;
            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: {Styles.buttonHoverBgColor};
        }}
        """)

        nextshadowEffect = QGraphicsDropShadowEffect()
        nextshadowEffect.setOffset(3, 3)
        nextshadowEffect.setBlurRadius(10)
        self.next_image_button = QPushButton("&Next", self)
        self.next_image_button.clicked.connect(self.showNextImage)
        self.next_image_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_image_button.setFocus(True)
        self.next_image_button.setGraphicsEffect(nextshadowEffect)
        self.next_image_button.setStyleSheet(f"""
        QPushButton {{
            width: 150px;
            height: 20px;
            border: 1px solid black;
            border-radius: {Styles.buttonBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
            font-weight: bold;
            font-size: 15px;

        }}
        QPushButton:hover {{
            background-color: {Styles.buttonHoverBgColor};
        }}
        """)

        self.image_counter_label = QLabel()
        self.image_counter_label.setStyleSheet("font-size: 20px;")
        self.image_counter_label.setText("0/0")

        right_control_buttons_layout = QHBoxLayout()
        right_control_buttons_layout.addWidget(self.previous_image_button)
        right_control_buttons_layout.addStretch()
        right_control_buttons_layout.addWidget(self.image_counter_label)
        right_control_buttons_layout.addStretch()
        right_control_buttons_layout.addWidget(self.next_image_button)

        right_layout.addLayout(right_control_buttons_layout)

        self.setLayout(right_layout)

        # Update Counter label
        self.image_counter_label.setText(self.galleryManager.getCounterString())

        self.stackedMediaWidget.setCurrentIndex(0)

    def showNextImage(self):
        self.galleryManager.setNextImage()
        self.image_counter_label.setText(self.galleryManager.getCounterString())

    def showPreviousImage(self):
        self.galleryManager.setPreviousImage()
        self.image_counter_label.setText(self.galleryManager.getCounterString())

    def setVideoWidget(self):
        self.stackedMediaWidget.setCurrentIndex(1)

    def setImageWidget(self):
        self.stackedMediaWidget.setCurrentIndex(0)