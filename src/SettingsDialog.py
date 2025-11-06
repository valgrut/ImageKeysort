from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QToolBar, QStyle, QDialog, QDialogButtonBox,
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QSpinBox, QCheckBox, QLabel,
    QHBoxLayout, QToolButton
)
import sys
from src.Styles import Styles

# Development notes:
#   When I tried to use "general" category, in the file, it was changed into
#   "%General" because of the internal "ini" file behaviour.
#   That caused, that Value could not be retrieved with "general".

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        self.setStyleSheet(f"""
            background-color: {Styles.widgetsBgColor};
        """)

        # Note: Do not use "General" category. Reserved by INI format.

        # --------- Widgets ---------
        # treeview behaviour
        # Options
        self.sp_nested_levels = QSpinBox()
        self.sp_nested_levels.setRange(1, 5)
        self.sp_nested_levels.setToolTip("How many nested shortcut folders to show in the UI.")

        # Form
        treeview_box = QGroupBox("Treeview behavior")
        treeview_form = QFormLayout()
        treeview_form.addRow("Shortcuts nested levels to show:", self.sp_nested_levels)
        treeview_box.setLayout(treeview_form)


        # shortcuts behaviour
        # options
        self.cb_allow_no_dest = QCheckBox("Allow shortcut to be added without selected destination path")

        # Form
        shortcuts_box = QGroupBox("Shortcuts behavior")
        shortcuts_form = QFormLayout()
        shortcuts_form.addRow(self.cb_allow_no_dest)
        shortcuts_box.setLayout(shortcuts_form)


        # Copy behaviour
        # Options
        self.cb_auto_next_after_copy = QCheckBox("Go to next image after copy")
        self.cb_other_opt1 = QCheckBox("Some other option 1")
        self.cb_other_opt2 = QCheckBox("Some other option 2")

        # Form
        copy_box = QGroupBox("Copy behaviour")
        copy_form = QFormLayout()
        copy_form.addRow(self.cb_auto_next_after_copy)
        copy_form.addRow(self.cb_other_opt1)
        copy_form.addRow(self.cb_other_opt2)
        copy_box.setLayout(copy_form)


        # Video
        # Options
        self.cb_mute_videos = QCheckBox("Mute videos by default")

        # Form
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
        root.addWidget(treeview_box)
        root.addWidget(shortcuts_box)
        root.addWidget(copy_box)
        root.addWidget(video_box)
        root.addWidget(self.buttons)
        self.setLayout(root)

        # Load settings on open
        self.load_settings()

    # ---------- Persistence ----------
    def load_settings(self):
        # Values have to be saved as a string, so the form state is restored
        # from the config file based on the saved "true" or "false" strings.
        settings = QSettings()

        settings.beginGroup("shortcuts")
        self.cb_allow_no_dest.setChecked(settings.value("allowNoDest") == "true")
        settings.endGroup()

        settings.beginGroup("treeview")
        self.sp_nested_levels.setValue(int(settings.value("nestedLevels", type=int)))
        settings.endGroup()

        settings.beginGroup("copy")
        self.cb_auto_next_after_copy.setChecked(settings.value("autoNextAfterCopy") == "true")
        self.cb_other_opt1.setChecked(settings.value("otherOpt1") == "true")
        self.cb_other_opt2.setChecked(settings.value("otherOpt2") == "true")
        settings.endGroup()

        settings.beginGroup("video")
        self.cb_mute_videos.setChecked(settings.value("muteDefault") == "true")
        settings.endGroup()

    def save_settings(self):
        # Values have to be saved as a string, so checking form state, and
        # based on that the "true" of "false" string is selected and saved.
        settings = QSettings()
        settings.beginGroup("shortcuts")
        settings.setValue("allowNoDest", "true" if self.cb_allow_no_dest.isChecked() else "false")
        settings.endGroup()

        settings.beginGroup("treeview")
        settings.setValue("nestedLevels", self.sp_nested_levels.value())
        settings.endGroup()

        settings.beginGroup("copy")
        settings.setValue("autoNextAfterCopy", "true" if self.cb_auto_next_after_copy.isChecked() else "false")
        settings.setValue("otherOpt1", "true" if self.cb_other_opt1.isChecked() else "false")
        settings.setValue("otherOpt2", "true" if self.cb_other_opt2.isChecked() else "false")
        settings.endGroup()

        settings.beginGroup("video")
        settings.setValue("muteDefault", "true" if self.cb_mute_videos.isChecked() else "false")
        settings.endGroup()

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

    @staticmethod
    def checkSetting(optionToRetrieve: str):
        settings = QSettings()
        if settings.contains(optionToRetrieve):
            return settings.value(optionToRetrieve)
        else:
            print(f"Setting {optionToRetrieve} does not exist in the Settings")
            return None

    @staticmethod
    def settingsGetNestingLevels() -> int:
        return SettingsDialog.checkSetting("treeview/nestedLevels")

    @staticmethod
    def settingsGetAllowNoDest() -> bool:
        return SettingsDialog.checkSetting("shortcuts/allowNoDest")

    @staticmethod
    def settingsGetAutoNextAfterCopy() -> bool:
        return SettingsDialog.checkSetting("copy/autoNextAfterCopy")

    @staticmethod
    def settingsGetMuteDefault() -> bool:
        return SettingsDialog.checkSetting("video/muteDefault")



