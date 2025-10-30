# settings_demo.py
import sys
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QToolBar, QDialog, QVBoxLayout,
    QGroupBox, QFormLayout, QSpinBox, QCheckBox, QDialogButtonBox, QWidget,
    QStyle, QMessageBox
)

ORG = "JP"                 # <- change as you like
APP = "ImageKeysort"       # <- change as you like

class SettingsDialog(QDialog):
    settingsChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(420)

        # --- Widgets ---------------------------------------------------------
        # General
        self.spn_nested_levels = QSpinBox()
        self.spn_nested_levels.setRange(1, 5)
        self.spn_nested_levels.setToolTip("How many nested shortcut levels to show.")
        self.chk_allow_shortcut_without_dest = QCheckBox(
            "Allow shortcut to be added without selected destination path"
        )

        grp_general = QGroupBox("General")
        lay_general = QFormLayout(grp_general)
        lay_general.addRow("Shortcuts nested levels to show", self.spn_nested_levels)
        lay_general.addRow(self.chk_allow_shortcut_without_dest)

        # Copy behaviour
        self.chk_go_next_after_copy = QCheckBox("Go to next image after copy")
        self.chk_other_opt_1 = QCheckBox("Some other option 1")
        self.chk_other_opt_2 = QCheckBox("Some other option 2")

        grp_copy = QGroupBox("Copy behaviour")
        lay_copy = QVBoxLayout(grp_copy)
        lay_copy.addWidget(self.chk_go_next_after_copy)
        lay_copy.addWidget(self.chk_other_opt_1)
        lay_copy.addWidget(self.chk_other_opt_2)

        # Video settings
        self.chk_mute_videos_default = QCheckBox("Mute videos by default")

        grp_video = QGroupBox("Video settings")
        lay_video = QVBoxLayout(grp_video)
        lay_video.addWidget(self.chk_mute_videos_default)

        # Buttons (OK/Cancel/Apply/Restore Defaults)
        self.btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel |
            QDialogButtonBox.Apply | QDialogButtonBox.RestoreDefaults
        )
        self.btns.accepted.connect(self._on_ok)
        self.btns.rejected.connect(self.reject)
        self.btns.button(QDialogButtonBox.Apply).clicked.connect(self._on_apply)
        self.btns.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self._on_restore_defaults)

        # Main layout
        root = QVBoxLayout(self)
        root.addWidget(grp_general)
        root.addWidget(grp_copy)
        root.addWidget(grp_video)
        root.addWidget(self.btns)

        # Load current values from QSettings
        self._settings = QSettings(ORG, APP)
        self.load_from_settings()

    # --- Settings schema helpers ---------------------------------------------
    def defaults(self) -> dict:
        return {
            "general/nested_levels": 2,
            "general/allow_shortcut_without_dest": True,
            "copy/go_next_after_copy": True,
            "copy/other_opt_1": False,
            "copy/other_opt_2": False,
            "video/mute_default": False,
        }

    def read_all(self) -> dict:
        d = self.defaults()
        out = {}
        for k, v in d.items():
            out[k] = self._settings.value(k, v, type=type(v))
        return out

    def write_all(self, values: dict):
        for k, v in values.items():
            self._settings.setValue(k, v)
        self._settings.sync()

    def load_from_settings(self):
        v = self.read_all()
        self.spn_nested_levels.setValue(v["general/nested_levels"])
        self.chk_allow_shortcut_without_dest.setChecked(v["general/allow_shortcut_without_dest"])
        self.chk_go_next_after_copy.setChecked(v["copy/go_next_after_copy"])
        self.chk_other_opt_1.setChecked(v["copy/other_opt_1"])
        self.chk_other_opt_2.setChecked(v["copy/other_opt_2"])
        self.chk_mute_videos_default.setChecked(v["video/mute_default"])

    def current_values(self) -> dict:
        return {
            "general/nested_levels": self.spn_nested_levels.value(),
            "general/allow_shortcut_without_dest": self.chk_allow_shortcut_without_dest.isChecked(),
            "copy/go_next_after_copy": self.chk_go_next_after_copy.isChecked(),
            "copy/other_opt_1": self.chk_other_opt_1.isChecked(),
            "copy/other_opt_2": self.chk_other_opt_2.isChecked(),
            "video/mute_default": self.chk_mute_videos_default.isChecked(),
        }

    # --- Button handlers ------------------------------------------------------
    def _apply(self):
        values = self.current_values()
        self.write_all(values)
        self.settingsChanged.emit(values)

    def _on_apply(self):
        self._apply()

    def _on_ok(self):
        self._apply()
        self.accept()

    def _on_restore_defaults(self):
        if QMessageBox.question(
            self, "Restore Defaults",
            "Reset all settings to default values?"
        ) == QMessageBox.Yes:
            self.write_all(self.defaults())
            self.load_from_settings()
            self.settingsChanged.emit(self.read_all())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Keysort (Demo)")
        self.resize(800, 500)
        self.settings = QSettings(ORG, APP)

        # --- Menu: Edit → Settings...
        edit_menu = self.menuBar().addMenu("&Edit")
        act_settings = QAction("Settings...", self)
        act_settings.setShortcut("Ctrl+,")  # common on mac; still nice on others
        act_settings.triggered.connect(self.open_settings)
        edit_menu.addAction(act_settings)

        # --- Toolbar with gear icon
        tb = QToolBar("Main Toolbar", self)
        self.addToolBar(tb)
        gear_icon = QIcon.fromTheme("preferences-system")
        if gear_icon.isNull():
            # fallback to a standard pixmap if theme icon not available
            gear_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        btn_settings = QAction(gear_icon, "Settings", self)
        btn_settings.triggered.connect(self.open_settings)
        tb.addAction(btn_settings)

        # --- Central placeholder
        central = QWidget()
        self.setCentralWidget(central)

        # Example: read a setting right away to drive behaviour (demo)
        self.apply_settings(self._read_all())

    def _read_all(self) -> dict:
        # mirror dialog helper
        defaults = {
            "general/nested_levels": 2,
            "general/allow_shortcut_without_dest": True,
            "copy/go_next_after_copy": True,
            "copy/other_opt_1": False,
            "copy/other_opt_2": False,
            "video/mute_default": False,
        }
        out = {}
        for k, v in defaults.items():
            out[k] = self.settings.value(k, v, type=type(v))
        return out

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.settingsChanged.connect(self.apply_settings)
        dlg.exec_()

    def apply_settings(self, s: dict):
        """
        React to setting changes here.
        Wire these keys into your app’s behaviour (navigation, copy flow, video player, etc).
        """
        # Examples (pseudo-usage comments):
        # - s["general/nested_levels"]: update your sidebar/tree depth
        # - s["copy/go_next_after_copy"]: toggle auto-advance after copy
        # - s["video/mute_default"]: set default mute on your video widget
        # For demo, just print:
        print("Settings applied:", s)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName(ORG)
    app.setApplicationName(APP)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

