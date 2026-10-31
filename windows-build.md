# How to build app on Windows

TODO - Merge into README ?

- **Considerations**:
    - You always need to compile your app on your target system. So, if you want to create a Mac .app you need to do this on a Mac, for an EXE you need to use Windows.


## 0. Run a windows-build script

Run in PowerShell:

`.\tools\build-windows.ps1`

DONE!

or - manually, follow steps 1-n ... :


## 1. Install python

- From: https://www.python.org/downloads/release/python-3126/
- Windows installer (64-bit)

and Check the "Add to PATH" option!


## 2. Open Powershell (not linux shell)

- We need to work on Windows's CLI, not linux subsystem one


## 3. Install pyinstaller and other dependencies (requirements.txt)

- Activate venv to keep the env clean:
```
py.exe -3.12 -m venv packenv
.\packenv\Scripts\python.exe -m pip install -r requirements.txt
.\packenv\Scripts\python.exe -m PyInstaller --clean --noconfirm ImageKeysort.spec
# .\packenv\scripts\activate.bat
```

- [OPTIONAL] Install dependencies:
    - TODO: Maybe not necessary now?
```
apt-get install pylint  # to run static code analysis before starting the build process
pip3 install pyinstaller
pip3 install PyInstaller   # if pyinstaller is not available
pip3 install PyQt5
pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib   # If problems with packaging
pip install --requirement requirements.txt
```


## 4. cd into app directory


## 5. Build the app

```
pyinstaller --onefile image-keysort.py
```

- Creates: `dist`, `build` and `spec` file
    - `build` contains files for build; bundling, results of analysis, logs, ...
    - `dist` contains files for distribution (exe, .dll libraries, ...)
    - `spec file`

- Building can be repeated using the specfile

```
pyinstaller.exe --noconfirm .\windows.spec
```

- Resulting .exe is in 'dist' directory.


## 6. Completing Windows installer

- 1. Download InstallForge from https://installforge.net/
- 2. 


## 7. Additional options

### 7.1. Turn off the CLI window behing the GUI

- Open .spec file
- set `console=False` under the EXE block


### 7.2. Create just 1 file containing everyting (libraries, exe...)

```
pyinstaller --onefile app.py
```

- the one-file build is easier to distribute
- slower to execute
    - because every time the application is run it must create a temporary folder to unpack the contents of the executable
- debugging a one file app is much harder
    - you should make sure everything is working with a normal build before you create a one-file package


### 7.3. Add icon to your app

```spec
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='blarh',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='hand.ico')
```

- and may be required to add this in the code:
    - `app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'hand.ico')))`


### 7.4. Add Taskbar Icons

- even if the icon is showing on the window, it may still not show on the taskbar

```
from PyQt5 import QtWidgets, QtGui
import sys, os

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class MainWindow(QtWidgets.QMainWindow):
    ...
    ...
```
