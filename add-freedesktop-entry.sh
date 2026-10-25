#! /usr/bin/env bash
#
# Creates a .desktop entry.
# Adds an app into the "open with" in the menus.

# Ref: https://unix.stackexchange.com/questions/103213/how-can-i-add-an-application-to-the-gnome-application-menu


# Single user:
SINGLE="~/.local/share/applications/image-keysort.desktop"

# Every system user:
# MULTI="/usr/share/applications/image-keysort.desktop"


touch "$SINGLE"

cat << EOF > "$SINGLE"
[Desktop Entry]
Type=Application
Name=Image Keysort
Comment=Sort and manage files in the directory with a keyboard
Icon=TODO_PATH_TO_REPO/Resources/icon.jpg
Path=TODO_PATH_TO_REPO
Exec=/usr/bin/python3 -m src.main
Terminal=false
Categories=Application;Utility

# This is the key part for “Open With” on folders:
MimeType=inode/directory;

# Optional
Icon=TODO_PATH_TO_REPO/Resources/icon.jpg %U
StartupNotify=true
EOF
