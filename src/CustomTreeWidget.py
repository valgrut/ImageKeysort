from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget


class CustomTreeWidget(QTreeWidget):

    def __init__(self):
        super().__init__()
