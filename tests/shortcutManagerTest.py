import unittest
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from src.MainWindow import MainWindow
from src.ShortcutManager import ShortcutManager  # Import the ShortcutManager class

app = QApplication([])  # needed for the app to work during testing

# Notes:
# - "test_" in the method name is required for unittest to recognize the test method

class TestShortcutManager(unittest.TestCase):
    def setUp(self):
        # Create the application window and button (the GUI to be tested)
        self.window = MainWindow()  # Replace with your actual window class
        self.galleryManager = self.window.galleryManager
        self.button = self.window.copyButton  # Example: the button you're testing

    def test_getAllPaths_simple(self):
        # Example test for getAllPaths
        shortcutsData = {
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
        manager = ShortcutManager(self.window)
        paths = manager.getAllPaths(shortcutsData)
        
        # Check if the paths returned are as expected
        self.assertEqual(paths, ["C:/image-sorter/testing-data/kk"])

    def test_getAllPaths_complex(self):
        shortcutsData = {
            "keys": {
                "w": {
                    "dst_path": "HOME/Gaming/The Witcher",
                    "keys": {}
                },
                "o": {
                    "dst_path": "HOME/Gaming/World of Warcraft",
                    "keys": {}
                },
                "c": {
                    "dst_path": "HOME/Gaming/Cyberpunk 2077",
                    "keys": {}
                },
                "m": {
                    "dst_path": "HOME/Memes/Gaming memes",
                    "keys": {
                        "f": {
                            "dst_path": "HOME/Memes/Gaming memes/Factorio",
                            "keys": {}
                        },
                        "e": {
                            "dst_path": "HOME/Memes/Gaming memes/Path of Exile",
                            "keys": {}
                        },
                        "w": {
                            "dst_path": "HOME/Memes/Gaming memes/The Witcher",
                            "keys": {}
                        },
                        "o": {
                            "dst_path": "HOME/Memes/Gaming memes/WoW",
                            "keys": {}
                        }
                    }
                },
                "g": {
                    "dst_path": "HOME/Gaming/Guild wars 2",
                    "keys": {}
                }
            }
        }
        manager = ShortcutManager(self.window)
        paths = manager.getAllPaths(shortcutsData)
        
        # Check if the paths returned are as expected
        self.assertEqual(paths, ["HOME/Gaming/The Witcher", "HOME/Gaming/World of Warcraft", "HOME/Gaming/Cyberpunk 2077", "HOME/Memes/Gaming memes", "HOME/Memes/Gaming memes/Factorio", "HOME/Memes/Gaming memes/Path of Exile", "HOME/Memes/Gaming memes/The Witcher", "HOME/Memes/Gaming memes/WoW", "HOME/Gaming/Guild wars 2"])

    # def test_toggleCoppyMode(self):
    #     # Check that copy mode is set to False
    #     self.assertEqual(self.window.copyOnly, False)  # Example assertion
        
    #     # Simulate clicking the button
    #     QTest.mouseClick(self.button, Qt.LeftButton)

    #     # Check if the button click did what it's supposed to do
    #     self.assertEqual(self.window.copyOnly, True)  # Example assertion

    def test_addShortcut_simple(self):
        pass

    def test_addShortcut_complex(self):
        pass

    def test_addKeyUnderCurrent(self):
        pass

    def test_addDstForShortcut(self):
        pass

    def test_getDstForShortcut(self):
        pass

    def test_removeShortcutSequence_simple(self):
        pass

    def test_removeShortcutSequence_complex(self):
        pass

    def test_getLastKey(self):
        pass
    
    def test_getLastKeyOfSequenceAndUpdate(self):
        pass

    def test_getLastPossibleKeyOfSequence(self):
        pass

    def tearDown(self):
        self.window.close()

if __name__ == '__main__':
    unittest.main()
