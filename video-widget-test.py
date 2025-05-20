from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl
import sys

class Window(QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties such as title, size, and icon
        self.setWindowTitle("Codeloop - PyQt5 Media Player")
        self.setGeometry(350, 100, 700, 500)
        self.setWindowIcon(QIcon('icon.png'))

        # Initialize the user interface
        self.init_ui()
        self.show()

    def init_ui(self):
        # Initialize media player and video widget
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videowidget = QVideoWidget()

        # Create buttons for controlling media playback
        openBtn = QPushButton('Open Video')
        openBtn.setStyleSheet(
            "QPushButton { background-color: #f0f0f0; border: 1px solid #707070; border-radius: 5px; padding: 5px; }"
            "QPushButton:hover { background-color: #e0e0e0; }"
        )
        openBtn.clicked.connect(self.open_file)

        self.playBtn = QPushButton('Play')
        self.playBtn.setStyleSheet(
            "QPushButton { background-color: #f0f0f0; border: 1px solid #707070; border-radius: 5px; padding: 5px; }"
            "QPushButton:hover { background-color: #e0e0e0; }"
        )
        self.playBtn.setEnabled(False)
        self.playBtn.clicked.connect(self.play_video)

        self.pauseBtn = QPushButton('Pause')
        self.pauseBtn.setStyleSheet(
            "QPushButton { background-color: #f0f0f0; border: 1px solid #707070; border-radius: 5px; padding: 5px; }"
            "QPushButton:hover { background-color: #e0e0e0; }"
        )
        self.pauseBtn.setEnabled(False)
        self.pauseBtn.clicked.connect(self.pause_video)

        self.stopBtn = QPushButton('Stop')
        self.stopBtn.setStyleSheet(
            "QPushButton { background-color: #f0f0f0; border: 1px solid #707070; border-radius: 5px; padding: 5px; }"
            "QPushButton:hover { background-color: #e0e0e0; }"
        )
        self.stopBtn.setEnabled(False)
        self.stopBtn.clicked.connect(self.stop_video)

        # Create sliders for seeking within the video and adjusting volume
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setStyleSheet(
            "QSlider::groove:horizontal { height: 6px; background: #f0f0f0; border: 1px solid #707070; border-radius: 3px; }"
            "QSlider::handle:horizontal { background: #007bff; border: 1px solid #0056b3; width: 14px; margin: -5px 0px; border-radius: 7px; }"
            "QSlider::add-page:horizontal { background: white; }"
            "QSlider::sub-page:horizontal { background: #007bff; }"
        )
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.set_position)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setStyleSheet(
            "QSlider::groove:horizontal { height: 6px; background: #f0f0f0; border: 1px solid #707070; border-radius: 3px; }"
            "QSlider::handle:horizontal { background: #007bff; border: 1px solid #0056b3; width: 14px; margin: -5px 0px; border-radius: 7px; }"
            "QSlider::add-page:horizontal { background: white; }"
            "QSlider::sub-page:horizontal { background: #007bff; }"
        )
        self.volumeSlider.setValue(100)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setToolTip("Volume")
        self.volumeSlider.valueChanged.connect(self.change_volume)

        # Create layout for arranging widgets horizontally
        hboxLayout = QHBoxLayout()
        hboxLayout.addWidget(openBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(self.pauseBtn)
        hboxLayout.addWidget(self.stopBtn)
        hboxLayout.addWidget(self.positionSlider)
        hboxLayout.addWidget(self.volumeSlider)

        # Create layout for arranging widgets vertically
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(hboxLayout)

        # Set the layout of the window
        self.setLayout(vboxLayout)
        self.mediaPlayer.setVideoOutput(videowidget)

        # Connect media player signals to their respective slots
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def open_file(self):
        # Open file dialog to select a video file
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filename != '':
            # Set the selected video file to the media player
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            # Enable playback control buttons
            self.playBtn.setEnabled(True)
            self.pauseBtn.setEnabled(True)
            self.stopBtn.setEnabled(True)

    def play_video(self):
        # Start playback
        self.mediaPlayer.play()

    def pause_video(self):
        # Pause playback
        self.mediaPlayer.pause()

    def stop_video(self):
        # Stop playback
        self.mediaPlayer.stop()

    def mediastate_changed(self, state):
        # Update button states based on media player state
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setEnabled(False)
            self.pauseBtn.setEnabled(True)
            self.stopBtn.setEnabled(True)
        else:
            self.playBtn.setEnabled(True)
            self.pauseBtn.setEnabled(False)
            self.stopBtn.setEnabled(False)

    def position_changed(self, position):
        # Update slider position based on current playback position
        self.positionSlider.setValue(position)

    def duration_changed(self, duration):
        # Set slider range based on total duration of the video
        self.positionSlider.setRange(0, duration)

    def set_position(self, position):
        # Set playback position based on slider value
        self.mediaPlayer.setPosition(position)

    def change_volume(self, volume):
        # Change media player volume based on slider value
        self.mediaPlayer.setVolume(volume)

# Create the application instance
app = QApplication(sys.argv)

# Create the main window instance
window = Window()

# Run the application event loop
sys.exit(app.exec_())
