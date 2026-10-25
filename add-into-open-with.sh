# Add Image Keysort into the context menu OpenWith on Fedora's File manager
# Right click on directory -> Open With -> Image Keysort

# Requires: desktop-file-utils

mkdir -p ~/.local/share/applications
touch ~/.local/share/applications/image-keysort.desktop

cat << EOF > ~/.local/share/applications/image-keysort.desktop
[Desktop Entry]
Type=Application
Name=Image Keysort
Comment=Sort images from a folder
# If you have a CLI entrypoint:
# Exec=image-keysort %U
# Or if you run a script directly:
Exec=TODO_PATH_TO_REPO/src/main.py %U
Terminal=false
Categories=Utility;

# This is the key part for “Open With” on folders:
MimeType=inode/directory;

# Optional (nice to have):
Icon=image-keysort
StartupNotify=true
EOF

desktop-file-validate ~/.local/share/applications/image-keysort.desktop
update-desktop-database ~/.local/share/applications
