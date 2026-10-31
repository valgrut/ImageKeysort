import os
import sys
import traceback
from pathlib import Path

# On Windows, set multimedia backend for videos to work.
if sys.platform.startswith("win"):
    os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"


def _crash_log_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "image-keysort-crash.log"
    return Path.cwd() / "image-keysort-crash.log"


def _excepthook(exc_type, exc, tb):
    text = "".join(traceback.format_exception(exc_type, exc, tb))
    try:
        _crash_log_path().write_text(text, encoding="utf-8")
    except OSError:
        pass
    sys.__excepthook__(exc_type, exc, tb)


sys.excepthook = _excepthook

import argparse
import logging

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QCoreApplication
except Exception:
    _crash_log_path().write_text(traceback.format_exc(), encoding="utf-8")
    raise

import src.resources_rc  # noqa: F401  registers Qt resources
from src.MainWindow import MainWindow


# Note: Pycharm: Shift + F10 always runs main.py. No need to always click to main.py first.


log = logging.getLogger(__name__)


def setupLogging(debugLevel):
    if getattr(sys, "frozen", False):
        log_file = Path(sys.executable).resolve().parent / "image-keysort.log"
    else:
        log_file = Path("image-keysort.log")

    logging.basicConfig(
        level=debugLevel,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ]
    )


def parseArguments():
    parser = argparse.ArgumentParser(
                    prog='Image Keysort',
                    description='Shortcut based image sorter.',
                    epilog='For CLI options, please refer to the documentation.')
    parser.add_argument('-c', '--set-copy-mode', action='store_true')  # on/off flag
    parser.add_argument('--src-path', type=str, required=False, help='Path to the source directory to load images from on startup')
    parser.add_argument('--presets-path', type=str, required=False, help='Path to the presets file (shortcuts data) to load on startup')
    args = parser.parse_args()
    return args


def main():
    QCoreApplication.setOrganizationName("JP")
    QCoreApplication.setOrganizationDomain("wogon.cz")
    QCoreApplication.setApplicationName("Image Keysort")

    from src.SettingsDialog import SettingsDialog
    SettingsDialog.initializeSettings()

    setupLogging(debugLevel=logging.DEBUG)

    parsedArgs = parseArguments()

    app = QApplication(sys.argv)
    window = MainWindow(args=parsedArgs)
    window.apply_settings()
    window.show()
    app.aboutToQuit.connect(window.shortcutManager.askSaveIfChanged)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
