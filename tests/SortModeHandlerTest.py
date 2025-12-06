import unittest

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QCoreApplication, QEvent

from src.main import main
from src.MainWindow import MainWindow


QCoreApplication.setOrganizationName("JP")
QCoreApplication.setOrganizationDomain("wogon.cz")
QCoreApplication.setApplicationName("Image Keysort")

app = QApplication([])  # needed for the app to work during testing

# Notes:
# - "test_" in the method name is required for unittest to recognize the test method

# TODO test:
# Ze je image presunut / zkopirovan / smazan z dst / src
# Ze je image vracen pri ctrl+z
# Sentinel
# InstantCopy mode (,;)
#
# Move mode:
# abcd
# ,ax
# ;ax
# <space>
# abc<esc>
# abc<enter>
# abc<enter>cde
# .
# <delete>
# ctrl+z
# abc<space>  # dst advice
#
# COPY mode:
# to samo co vyse

class TestSortModeHandler(unittest.TestCase):
    def setUp(self):
        # Create the application window and button (the GUI to be tested)
        self.window = MainWindow()  # Replace with your actual window class
        # self.sm = ShortcutManager(self.window)
        # self.galleryManager = self.window.galleryManager
        # self.button = self.window.copyButton  # Example: the button you're testing
        self.window.set_sort_mode()
        self.window.shortcutManager.shortcutTree = {
            "keys": {
                "a": {
                    "dst_path": "",
                    "keys": {
                        "a": {
                            "dst_path": "C:/image-sorter/testing-data/kk",
                            "keys": {}
                        }
                    }
                }
            }
        }

    def test_simple(self):
        QTest.keySequence(self.window, Qt.Key_A)
        self.assertEqual(self.window.sortModeHandler.keySeq, "a")

        QTest.keySequence(self.window, Qt.Key_Escape)
        self.assertEqual(self.window.sortModeHandler.keySeq, "")

        QTest.keySequence(self.window, Qt.Key_A)
        QTest.keySequence(self.window, Qt.Key_A)
        self.assertEqual(self.window.sortModeHandler.keySeq, "")

        # Check if the paths returned are as expected
        # self.assertEqual(paths, ["C:/image-sorter/testing-data/kk"])


    # def test_getAllPaths_complex(self):
    #     shortcutsData = {
    #         "keys": {
    #             "w": {
    #                 "dst_path": "HOME/Gaming/The Witcher",
    #                 "keys": {}
    #             },
    #             "o": {
    #                 "dst_path": "HOME/Gaming/World of Warcraft",
    #                 "keys": {}
    #             },
    #             "c": {
    #                 "dst_path": "HOME/Gaming/Cyberpunk 2077",
    #                 "keys": {}
    #             },
    #             "m": {
    #                 "dst_path": "HOME/Memes/Gaming memes",
    #                 "keys": {
    #                     "f": {
    #                         "dst_path": "HOME/Memes/Gaming memes/Factorio",
    #                         "keys": {}
    #                     },
    #                     "e": {
    #                         "dst_path": "HOME/Memes/Gaming memes/Path of Exile",
    #                         "keys": {}
    #                     },
    #                     "w": {
    #                         "dst_path": "HOME/Memes/Gaming memes/The Witcher",
    #                         "keys": {}
    #                     },
    #                     "o": {
    #                         "dst_path": "HOME/Memes/Gaming memes/WoW",
    #                         "keys": {}
    #                     }
    #                 }
    #             },
    #             "g": {
    #                 "dst_path": "HOME/Gaming/Guild wars 2",
    #                 "keys": {}
    #             }
    #         }
    #     }
    #     manager = ShortcutManager(self.window)
    #     paths = manager.getAllPaths(shortcutsData)
    #
    #     # Check if the paths returned are as expected
    #     self.assertEqual(paths, ["HOME/Gaming/The Witcher", "HOME/Gaming/World of Warcraft", "HOME/Gaming/Cyberpunk 2077", "HOME/Memes/Gaming memes", "HOME/Memes/Gaming memes/Factorio", "HOME/Memes/Gaming memes/Path of Exile", "HOME/Memes/Gaming memes/The Witcher", "HOME/Memes/Gaming memes/WoW", "HOME/Gaming/Guild wars 2"])
    #     self.sm.clearShortcuts()


    # def test_toggleCoppyMode(self):
    #     # Check that copy mode is set to False
    #     self.assertEqual(self.window.copyOnly, False)  # Example assertion

    #     # Simulate clicking the button
    #     QTest.mouseClick(self.button, Qt.LeftButton)

    #     # Check if the button click did what it's supposed to do
    #     self.assertEqual(self.window.copyOnly, True)  # Example assertion


    # ========== addShortcut ==========
    # def test_addShortcut_no_dst(self):
    #     sm = ShortcutManager(self.window)
    #     sm.addShortcutSequence("a")
    #     self.assertIn('a', sm.shortcutTree['keys'])
    #     self.assertEqual(sm.areShortcutsModified(), True)