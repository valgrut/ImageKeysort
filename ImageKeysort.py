"""Windows packaging entry point.

PyInstaller must not use src/main.py as the script: that puts `src` on
sys.path and breaks `import src.*` inside the frozen app.
"""

from src.main import main

if __name__ == "__main__":
    main()
