import os
import sys

# On Windows, set multimedia backend for videos to work.
if sys.platform.startswith("win"):
    os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"

import argparse
import pathlib
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication
from src.MainWindow import MainWindow


# Note: Pycharm: Shift + F10 always runs main.py. No need to always click to main.py first.


log = logging.getLogger(__name__)


def setupLogging(debugLevel):
    logging.basicConfig(
        level=debugLevel,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("image-keysort.log")
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

    # srcPathArg = args.src_path
    # presetsArg = args.presets_path
    # setCopyModeArg = args.set_copy_mode
    return args


def main():
    QCoreApplication.setOrganizationName("JP")
    QCoreApplication.setOrganizationDomain("wogon.cz")
    QCoreApplication.setApplicationName("Image Keysort")

    # # Initialize Settings on first run to prevent non-existing config
    from src.SettingsDialog import SettingsDialog
    SettingsDialog.initializeSettings()

    # Build qss file on the start (in case app started without Makefile)
    # TODO: Does not work:
    # import qtsass
    # scss_path = pathlib.Path("static/app-styles.scss")
    # qss_path = pathlib.Path("static/app-styles.qss")
    # qss = qtsass.compile(scss_path.read_text(encoding="utf-8"))
    # qss_path.write_text(qss, encoding="utf-8")

    # Config logging
    setupLogging(debugLevel=logging.WARNING and logging.INFO and logging.DEBUG)

    # CLI arguments parsing
    parsedArgs = parseArguments()

    # Create app and apply theme
    app = QApplication(sys.argv)
    window = MainWindow(args=parsedArgs)
    window.apply_settings()
    window.show()
    app.aboutToQuit.connect(window.shortcutManager.askSaveIfChanged)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

