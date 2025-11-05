from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QToolBar, QStyle, QDialog, QDialogButtonBox,
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QSpinBox, QCheckBox, QLabel,
    QHBoxLayout, QToolButton
)
import sys

## TODO: check, rewrite by myself...

ORG = "JP"
APP = "ImageKeysort"


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        # --------- Widgets ---------
        # General
        self.sp_nested_levels = QSpinBox()
        self.sp_nested_levels.setRange(1, 5)
        self.sp_nested_levels.setToolTip("How many nested shortcut folders to show in the UI.")
        self.cb_allow_no_dest = QCheckBox("Allow shortcut to be added without selected destination path")

        general_box = QGroupBox("General settings")
        gen_form = QFormLayout()
        gen_form.addRow("Shortcuts nested levels to show:", self.sp_nested_levels)
        gen_form.addRow(self.cb_allow_no_dest)
        general_box.setLayout(gen_form)

        # Copy behaviour
        self.cb_auto_next_after_copy = QCheckBox("Go to next image after copy")
        self.cb_other_opt1 = QCheckBox("Some other option 1")
        self.cb_other_opt2 = QCheckBox("Some other option 2")

        copy_box = QGroupBox("Copy behaviour")
        copy_form = QFormLayout()
        copy_form.addRow(self.cb_auto_next_after_copy)
        copy_form.addRow(self.cb_other_opt1)
        copy_form.addRow(self.cb_other_opt2)
        copy_box.setLayout(copy_form)

        # Video
        self.cb_mute_videos = QCheckBox("Mute videos by default")

        video_box = QGroupBox("Video settings")
        video_form = QFormLayout()
        video_form.addRow(self.cb_mute_videos)
        video_box.setLayout(video_form)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)

        # Layout
        root = QVBoxLayout()
        root.addWidget(general_box)
        root.addWidget(copy_box)
        root.addWidget(video_box)
        root.addWidget(self.buttons)
        self.setLayout(root)

        # Load settings on open
        self.load_settings()

        # print(QSettings(ORG, APP).allKeys())  # AHAAA, takhle. To je opravdu globalne pristupne!!! TODO pouzit.

    # ---------- Persistence ----------
    def load_settings(self):
        s = QSettings(ORG, APP)
        self.sp_nested_levels.setValue(int(s.value("general/nestedLevels", 2)))
        self.cb_allow_no_dest.setChecked(s.value("general/allowNoDest", "false") == "true")

        self.cb_auto_next_after_copy.setChecked(s.value("copy/autoNextAfterCopy", "true") == "true")
        self.cb_other_opt1.setChecked(s.value("copy/otherOpt1", "false") == "true")
        self.cb_other_opt2.setChecked(s.value("copy/otherOpt2", "false") == "true")

        self.cb_mute_videos.setChecked(s.value("video/muteDefault", "false") == "true")

        # settings = QSettings("/home/petra/misc/myapp.ini", QSettings.IniFormat)

    def save_settings(self):
        s = QSettings(ORG, APP)
        s.setValue("general/nestedLevels", self.sp_nested_levels.value())
        s.setValue("general/allowNoDest", "true" if self.cb_allow_no_dest.isChecked() else "false")

        s.setValue("copy/autoNextAfterCopy", "true" if self.cb_auto_next_after_copy.isChecked() else "false")
        s.setValue("copy/otherOpt1", "true" if self.cb_other_opt1.isChecked() else "false")
        s.setValue("copy/otherOpt2", "true" if self.cb_other_opt2.isChecked() else "false")

        s.setValue("video/muteDefault", "true" if self.cb_mute_videos.isChecked() else "false")

    def restore_defaults(self):
        # Define your app’s sensible defaults here
        self.sp_nested_levels.setValue(2)
        self.cb_allow_no_dest.setChecked(False)
        self.cb_auto_next_after_copy.setChecked(True)
        self.cb_other_opt1.setChecked(False)
        self.cb_other_opt2.setChecked(False)
        self.cb_mute_videos.setChecked(False)

    # Make sure clicking OK persists
    def accept(self):
        self.save_settings()
        super().accept()


