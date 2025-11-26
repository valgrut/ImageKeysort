import os
import shutil
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLineEdit, QLineEdit, QPushButton
from PyQt5.QtTest import QTest
from pytestqt.qtbot import QtBot

from src.main import main
from src.MainWindow import MainWindow

# TODO: Fix

def test_end_to_end_app(qtbot: QtBot, tmp_path: Path):
    """
    End-to-end test for the app:
    1. Set edit mode (Ctrl + E)
    2. Add a shortcut with keychars `fc` and a destination path
    3. Open the gallery
    4. Press `fc` to move the current image to the destination directory
    5. Verify the image is in the destination directory
    """
    # Step 1: Start the app
    main_window = MainWindow()
    qtbot.addWidget(main_window)
    main_window.show()

    # Create a temporary image and destination directory
    src_dir = tmp_path / "gallery"
    dst_dir = tmp_path / "destination"
    src_dir.mkdir()
    dst_dir.mkdir()

    # Create a dummy image in the source directory
    image_path = src_dir / "test_image.jpg"
    with open(image_path, "wb") as f:
        f.write(b"dummy_image_data")

    # Step 2: Set edit mode (Ctrl + E)
    QTest.keyClick(main_window, Qt.Key_E, Qt.ControlModifier)

    # Step 3: Add a shortcut with keychars `fc` and destination path
    # Simulate typing `fc` and pressing Enter
    QTest.keyClicks(main_window, "fc")
    QTest.keyClick(main_window, Qt.Key_Return)

    # Simulate providing the destination path in the dialog
    dialog = main_window.findChild(QDialog)  # Assuming the dialog is a QDialog
    assert dialog is not None, "Shortcut dialog did not appear"
    dst_input = dialog.findChild(QLineEdit)  # Assuming the input is a QLineEdit
    assert dst_input is not None, "Destination input field not found"
    dst_input.setText(str(dst_dir))
    save_button = dialog.findChild(QPushButton, "saveButton")  # Assuming the save button has an object name
    assert save_button is not None, "Save button not found"
    qtbot.mouseClick(save_button, Qt.LeftButton)

    # Step 4: Open the gallery
    gallery_button = main_window.findChild(QPushButton, "galleryButton")  # Assuming the gallery button has an object name
    assert gallery_button is not None, "Gallery button not found"
    qtbot.mouseClick(gallery_button, Qt.LeftButton)

    # Step 5: Press `fc` to move the current image to the destination directory
    QTest.keyClicks(main_window, "fc")

    # Step 6: Verify the image is in the destination directory
    moved_image_path = dst_dir / "test_image.jpg"
    assert moved_image_path.exists(), f"Image was not moved to {dst_dir}"

    # Cleanup (optional)
    shutil.rmtree(tmp_path)