from pathlib import Path
import os
import qtsass
from PyInstaller.utils.hooks import collect_submodules

# Prevent this .spec file be run on non-Windows systems
if os.name != 'nt':
  print("Not a Windows OS, exiting...")
  exit(1)


# SPECPATH is provided by PyInstaller while evaluating this file.
ROOT_DIR = Path(SPECPATH).resolve()
SRC_DIR = ROOT_DIR / "src"


# ===== css styles compilation =====

STATIC_DIR = ROOT_DIR / "static"
SCSS_FILE = STATIC_DIR / "app-styles.scss"
QSS_FILE = STATIC_DIR / "app-styles.qss"

qtsass.compile_filename(SCSS_FILE, QSS_FILE)


# ===== Resources compilation =====
# TODO: Make all icons working
RESOURCES_DIR = ROOT_DIR / "Resources"
# pyrcc5 ${ROOT_DIR}/resources.qrc -o ${ROOT_DIR}/src/resources_rc.py; \


a = Analysis(
    [str(SRC_DIR / "main.py")],
    pathex=[str(ROOT_DIR)],
    binaries=[],
    datas=[
        (RESOURCES_DIR, "Resources"),
        (QSS_FILE, "static"),
        ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    exclude_binaries=True,
    name='image-keysort',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(RESOURCES_DIR / "icon.jpg"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="image-keysort",
)
