import unittest
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from main import MainWindow  # Import main.py from the src package

app = QApplication([])  # needed for the app to work during testing

class TestMyApp(unittest.TestCase):
    def setUp(self):
        # Create the application window and button (the GUI to be tested)
        self.window = MainWindow()  # Replace with your actual window class
        self.galleryManager = self.window.galleryManager
        self.button = self.window.copy_button  # Example: the button you're testing

    def test_button_click(self):
        # Check that copy mode is set to False
        self.assertEqual(self.window.copyOnly, False)  # Example assertion
        
        # Simulate clicking the button
        QTest.mouseClick(self.button, Qt.LeftButton)

        # Check if the button click did what it's supposed to do
        self.assertEqual(self.window.copyOnly, True)  # Example assertion

    def tearDown(self):
        self.window.close()

if __name__ == '__main__':
    unittest.main()
