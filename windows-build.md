# How to build app on Windows

## 1. Install python 
- From: https://www.python.org/downloads/release/python-3126/
- Windows installer (64-bit)

and Check the "Add to PATH" option!


## 2. Open Powershell

## 3. Install pyinstaller and other dependencies (requirements.txt)

pip3 install pyinstaller
pip install --requirement requirements.txt

## 4. cd into app directory

cd C:\Users\Kyuubi\Repositories\WorkstationSetup\scripts\image-sorter

## 5. Build the app

pyinstaller --onefile image-keysort.py


## 6. Resulting .exe should be in 'dist' directory.


