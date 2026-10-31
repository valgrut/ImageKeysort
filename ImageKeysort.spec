# ImageKeysort.spec
from pathlib import Path
import os
import subprocess
import sys

from PyInstaller.utils.hooks import collect_submodules

if os.name != "nt":
    raise SystemExit("Build this Windows executable on Windows.")

if sys.version_info >= (3, 13):
    raise SystemExit(
        "PyQt5 cannot load on Python 3.13 on this machine "
        "(DLL load failed for QtCore/QtWidgets). "
        "Build with Python 3.12, for example:\n"
        "  py -3.12 -m venv packenv\n"
        "  .\\packenv\\Scripts\\python.exe -m pip install -r requirements.txt\n"
        "  .\\packenv\\Scripts\\python.exe -m PyInstaller --clean --noconfirm ImageKeysort.spec\n"
        "or run tools\\build-windows.ps1"
    )

import qtsass

ROOT = Path(SPECPATH).resolve()
SRC = ROOT / "src"
STATIC = ROOT / "static"
ICON_FILE = ROOT / "Resources" / "icon.ico"

qtsass.compile_filename(
    str(STATIC / "app-styles.scss"),
    str(STATIC / "app-styles.qss"),
)

subprocess.run(
    [
        sys.executable,
        "-m", "PyQt5.pyrcc_main",
        str(ROOT / "resources.qrc"),
        "-o", str(SRC / "resources_rc.py"),
    ],
    cwd=str(ROOT),
    check=True,
)

a = Analysis(
    [str(ROOT / "ImageKeysort.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "Resources"), "Resources"),
        (str(STATIC), "static"),
        (str(ROOT / "about.html"), "."),
        (str(ROOT / "keyboard_shortcuts.html"), "."),
    ],
    hiddenimports=[
        "pkgutil",
        "src",
        *collect_submodules("src"),
        "PyQt5.QtMultimedia",
        "PyQt5.QtMultimediaWidgets",
        "PIL",
        "pytesseract",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "pytestqt"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ImageKeysort",
    icon=str(ICON_FILE),
    console=False,  # Set True to enable debug console output
    debug=False,
    strip=False,
    upx=False,
    contents_directory="_internal",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="ImageKeysort",
    strip=False,
    upx=False,
)
