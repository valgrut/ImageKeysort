import logging
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QGroupBox, QFormLayout, QSpinBox, QCheckBox, QComboBox)

from src.Styles import Styles

# Development notes:
#   When I tried to use "general" category, in the file, it was changed into
#   "%General" because of the internal "ini" file behaviour.
#   That caused, that Value could not be retrieved with "general".

log = logging.getLogger(__name__)


class SettingsDialog(QDialog):

    settingsChangedSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        # self.setStyleSheet(f"""
        #     background-color: {Styles.widgetsBgColor};
        # """)

        # Note: Do not use "General" category. Reserved by INI format.

        # --------- Widgets ---------
        # treeview behaviour
        # Options
        self.sp_nested_levels = QSpinBox()
        self.sp_nested_levels.setRange(1, 5)
        self.sp_nested_levels.setToolTip("How many nested shortcut folders to show in the UI.")
        self.cfg_load_last_preset = QCheckBox("Load preset from the last session on start.")
        self.cfg_show_only_key_subtree = QCheckBox("Show only shortcut subtree based on the current keychar sequence.")


        # Form
        treeview_box = QGroupBox("Treeview behavior")
        treeview_form = QFormLayout()
        treeview_form.addRow("Shortcuts nested levels to show:", self.sp_nested_levels)
        treeview_form.addRow(self.cfg_load_last_preset)
        treeview_form.addRow(self.cfg_show_only_key_subtree)
        treeview_box.setLayout(treeview_form)


        # shortcuts behaviour
        # options
        self.cb_allow_no_dest = QCheckBox("Allow shortcut to be added without selected destination path")
        self.cfg_confirm_to_override = QCheckBox("Ask for confirmation before overwriting the existing shortcut's destination path")
        self.cfg_sort_shortcuts = QCheckBox("Sort shortcuts alphabetically. Default: by insertion order")

        # Form
        shortcuts_box = QGroupBox("Shortcuts behavior")
        shortcuts_form = QFormLayout()
        shortcuts_form.addRow(self.cb_allow_no_dest)
        shortcuts_form.addRow(self.cfg_confirm_to_override)
        shortcuts_form.addRow(self.cfg_sort_shortcuts)
        shortcuts_box.setLayout(shortcuts_form)


        # Copy behaviour
        # Options
        self.cb_auto_next_after_copy = QCheckBox("Go to next image after copy")
        self.cb_other_opt1 = QCheckBox("Some other option 1")
        self.cb_other_opt2 = QCheckBox("Some other option 2")

        # Form
        copy_box = QGroupBox("Copy-mode behaviour")
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


        # Stylesheets
        self.cfg_app_theme = QComboBox()
        self.cfg_app_theme.addItem("Light")
        self.cfg_app_theme.addItem("Dark")
        self.cfg_app_theme.addItem("Night")
        self.cfg_app_theme.addItem("Retro")
        # TODO: Maybe, load themes from some directory so users can add custom themes without requiring code change.

        # Form
        themes_box = QGroupBox("Themes settings")
        themes_form = QFormLayout()
        themes_form.addRow(self.cfg_app_theme)
        themes_box.setLayout(themes_form)

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
        root.addWidget(themes_box)
        root.addWidget(self.buttons)
        self.setLayout(root)

        # Load settings on open
        self.load_settings()

    def load_settings(self):
        """
        Values have to be saved as a string, so the form state is restored
        from the config file based on the saved "true" or "false" strings.
        """

        settings = QSettings()

        settings.beginGroup("shortcuts")
        self.cb_allow_no_dest.setChecked(settings.value("allowNoDest") == "true")
        self.cfg_confirm_to_override.setChecked(settings.value("confirmToOverride") == "true")
        self.cfg_sort_shortcuts.setChecked(settings.value("sortShortcuts") == "true")
        settings.endGroup()

        settings.beginGroup("treeview")
        self.sp_nested_levels.setValue(int(settings.value("nestedLevels", type=int)))
        self.cfg_show_only_key_subtree.setChecked(settings.value("showSubtreeOnly") == "true")
        settings.endGroup()

        settings.beginGroup("copy")
        self.cb_auto_next_after_copy.setChecked(settings.value("autoNextAfterCopy") == "true")
        self.cb_other_opt1.setChecked(settings.value("otherOpt1") == "true")
        self.cb_other_opt2.setChecked(settings.value("otherOpt2") == "true")
        settings.endGroup()

        settings.beginGroup("video")
        self.cb_mute_videos.setChecked(settings.value("muteDefault") == "true")
        settings.endGroup()

        settings.beginGroup("theme")
        themeIndex = self.cfg_app_theme.findText(settings.value("currentTheme", defaultValue="Light"))
        self.cfg_app_theme.setCurrentIndex(themeIndex if themeIndex >= 0 else 0)
        settings.endGroup()


    def save_settings(self):
        """
        Values have to be saved as a string, so checking form state, and
        based on that the "true" of "false" string is selected and saved.
        """

        settings = QSettings()
        settings.beginGroup("shortcuts")
        settings.setValue("allowNoDest", "true" if self.cb_allow_no_dest.isChecked() else "false")
        settings.setValue("confirmToOverride", "true" if self.cfg_confirm_to_override.isChecked() else "false")
        settings.setValue("sortShortcuts", "true" if self.cfg_sort_shortcuts.isChecked() else "false")
        settings.endGroup()

        settings.beginGroup("treeview")
        settings.setValue("nestedLevels", int(self.sp_nested_levels.value()))
        settings.setValue("showSubtreeOnly", "true" if self.cfg_show_only_key_subtree.isChecked() else "false")
        settings.endGroup()

        settings.beginGroup("copy")
        settings.setValue("autoNextAfterCopy", "true" if self.cb_auto_next_after_copy.isChecked() else "false")
        settings.setValue("otherOpt1", "true" if self.cb_other_opt1.isChecked() else "false")
        settings.setValue("otherOpt2", "true" if self.cb_other_opt2.isChecked() else "false")
        settings.endGroup()

        settings.beginGroup("video")
        settings.setValue("muteDefault", "true" if self.cb_mute_videos.isChecked() else "false")
        settings.endGroup()

        settings.beginGroup("theme")
        settings.setValue("currentTheme", self.cfg_app_theme.currentText())
        settings.endGroup()


    @pyqtSlot()
    def restore_defaults(self):
        self.sp_nested_levels.setValue(3)
        self.cb_allow_no_dest.setChecked(True)
        self.cfg_confirm_to_override.setChecked(False)
        self.cfg_sort_shortcuts.setChecked(True)
        self.cfg_show_only_key_subtree.setChecked(True)
        self.cb_auto_next_after_copy.setChecked(True)
        self.cb_other_opt1.setChecked(False)
        self.cb_other_opt2.setChecked(False)
        self.cb_mute_videos.setChecked(True)
        self.cfg_app_theme.setCurrentText("Light")


    @staticmethod
    def initializeSettings():
        """
        Create initial settings if they do not exist yet.

        Called on application start, so some settings are always present.
        """
        try:
            SettingsDialog.settingsGetNestingLevels()
        except:
            log.info("Settings do not exist yet, creating default settings.")
            settings = QSettings()
            settings.beginGroup("shortcuts")
            settings.setValue("allowNoDest", "true")
            settings.setValue("confirmToOverride", "true")
            settings.setValue("sortShortcuts", "true")
            settings.endGroup()

            settings.beginGroup("treeview")
            settings.setValue("nestedLevels", 4)
            settings.setValue("showSubtreeOnly", "true")
            settings.endGroup()

            settings.beginGroup("copy")
            settings.setValue("autoNextAfterCopy", "true")
            settings.setValue("otherOpt1", "true")
            settings.setValue("otherOpt2", "true")
            settings.endGroup()

            settings.beginGroup("video")
            settings.setValue("muteDefault", "true")
            settings.endGroup()

            settings.beginGroup("theme")
            settings.setValue("currentTheme", "Light")
            settings.endGroup()

    # Make sure clicking OK persists
    def accept(self):
        self.save_settings()
        super().accept()
        self.settingsChangedSignal.emit()


    @staticmethod
    def _checkSetting(optionToRetrieve: str):
        settings = QSettings()

        if settings.contains(optionToRetrieve):
            return settings.value(optionToRetrieve)
        else:
            log.info(f"Setting {optionToRetrieve} does not exist in the Settings")
            return None
    
    @staticmethod
    def settingsGetNestingLevels() -> int:
        return int(SettingsDialog._checkSetting("treeview/nestedLevels"))

    @staticmethod
    def settingsGetShowSubtreeOnly() -> bool:
        # return SettingsDialog.checkSetting("shortcuts/allowNoDest")
        return True if SettingsDialog._checkSetting("treeview/showSubtreeOnly") == "true" else False

    @staticmethod
    def settingsGetAllowNoDest() -> bool:
        # return SettingsDialog.checkSetting("shortcuts/allowNoDest")
        return True if SettingsDialog._checkSetting("shortcuts/allowNoDest") == "true" else False

    @staticmethod
    def settingsGetConfirmToOverride() -> bool:
        # return SettingsDialog.checkSetting("shortcuts/confirmToOverride")
        return True if SettingsDialog._checkSetting("shortcuts/confirmToOverride") == "true" else False

    @staticmethod
    def settingsGetSortShortcuts() -> bool:
        # return SettingsDialog.checkSetting("shortcuts/sortShortcuts")
        return True if SettingsDialog._checkSetting("shortcuts/sortShortcuts") == "true" else False

    @staticmethod
    def settingsGetAutoNextAfterCopy() -> bool:
        # return SettingsDialog.checkSetting("copy/autoNextAfterCopy")
        return True if SettingsDialog._checkSetting("copy/autoNextAfterCopy") == "true" else False

    @staticmethod
    def settingsGetMuteDefault() -> bool:
        # TODO: Sakra, takhle to nebude fungovat, protoze to vraci ten string
        # Prozatimni reseni. Mozna udelat druhou tridu jako Config, ze ktere se
        # to pak bude brat. Ta bude staticka a staticky se zavola i to
        # load_config().
        return True if SettingsDialog._checkSetting("video/muteDefault") == "true" else False
        # return self.cb_mute_videos

    @staticmethod
    def settingsGetTheme() -> str:
        return SettingsDialog._checkSetting("theme/currentTheme")



