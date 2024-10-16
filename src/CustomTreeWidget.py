from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget


class CustomTreeWidget(QTreeWidget):
    def keyPressEvent(self, event):
        # Block left and right arrow keys from affecting QTreeWidget behavior
        if event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
            event.ignore()  # Ignore the event for QTreeWidget
        else:
            # Handle other keys normally
            super().keyPressEvent(event)