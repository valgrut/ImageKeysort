import sys
from PIL import Image

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)
from PyQt5.QtGui import QPixmap, QKeyEvent

# pip3 install pyqt5
# pip3 install keyboard

width = 1152
height = 864

class Shortcuts():
    def __init__(self):
        self.shortcuts = {"major": {}}
        
        """ 
        major: 
         x: <dst_path1>
          y: <dst_path2> 
        """
    
    def printShortcuts():
        pass

    def addShortcut():
        pass

    def addSubShortcut():
        pass
    
    def removeShortcut():
        pass

    def removeSubShortcut():
        pass

    def getPathOfShortcut():
        pass

    def isShortcutExist():
        pass

    def saveShortcuts():
        pass

    def loadShortcuts():
        pass

class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel(self)
        pixmap = QPixmap('networking.jpg')
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quick Picture sorter")
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

        layout = QHBoxLayout()


        widget = QWidget()
        widget.setLayout(layout)
        # Set the central widget of the Window.
        self.setCentralWidget(widget)
        gallery_source_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        print(gallery_source_directory)
        
        # button1 = QPushButton("Press Me!")
        imagewidget = ImageWidget()
        # layout.addWidget(button1)
        self.key_label = QLabel("Last Key Pressed: None", widget)

        layout.addWidget(self.key_label)
        layout.addWidget(imagewidget)


    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent):
            key_text = event.text()
            self.key_label.setText(f"Last Key Pressed: {key_text}")


def main():
    print("Hello World!")
    #img = Image.open("/home/jpeska/Downloads/7ton85.jpg")
    #img.show()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

