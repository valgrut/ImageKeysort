from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize

import src.resources_rc

class TreeItemWithButtons(QWidget):
    """
    tree item containing buttons to remove or edit item
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        editPixmap = QPixmap(":/Resources/edit.png")
        editIcon = QIcon(editPixmap)

        deletePixmap = QPixmap(":/Resources/bin.png")
        deleteIcon = QIcon(deletePixmap)

        editButton = QPushButton("E", self)
        # edit_button.setStyleSheet("max-width: 10px; border: 1px solid black; :hover {background-color: green;};")
        editButton.setStyleSheet("""
            QPushButton {
                max-width: 13px;
                width: 13px;
                background-color: transparent;
                border: 1px solid black;
                border-radius: 3px;
                color: black;  /* Set the initial text color */
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.5);  /* Solid color on hover */
                color: white;  /* Change text color on hover */
            }
        """)
        editButton.setIcon(editIcon)
        editButton.setIconSize(editButton.size())  # - QSize(5, 5))

        deleteButton = QPushButton("D", self)
        # delete_button.setStyleSheet("max-width: 10px")
        deleteButton.setStyleSheet(
        """
            QPushButton {
                max-width: 13px;
                width: 13px;
                background-color: transparent;
                border: 1px solid black;
                border-radius: 3px;
                color: black;  /* Set the initial text color */
                background-color: rgba(100, 0, 0, 0.3);  /* Solid color on hover */
            }
            QPushButton:hover {
                background-color: rgba(200, 0, 0, 1);  /* Solid color on hover */
                color: white;  /* Change text color on hover */
            }
        """)
        deleteButton.setIcon(deleteIcon)
        deleteButton.setIconSize(deleteButton.size())

        # TODO: this does not work:
        # self.setStyleSheet("background-color: green; border: 1px solid black;")
        self.setStyleSheet("background-color: green;")

        # self.setStyleSheet(
        # """
        #     TreeItemWithButtons {
        #         xbackground-color: transparent;
        #         border: 1px solid black;
        #         xborder-radius: 3px;
        #         xcolor: black;  /* Set the initial text color */
        #         xbackground-color: rgba(100, 0, 0, 0.3);  /* Solid color on hover */
        #     }
        #     TreeItemWithButtons:hover {
        #         background-color: rgba(200, 0, 0, 1);  /* Solid color on hover */
        #         color: white;  /* Change text color on hover */
        #     }
        # """)

        layout.addWidget(editButton)
        layout.addWidget(deleteButton)
        layout.addStretch()

        self.setLayout(layout)