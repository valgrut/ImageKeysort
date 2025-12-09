# Image Keysort

## 1. Description

Do you have directory with hundreds of screenshots, where every image belongs to different directory?

And even the thought of the repetitive sequence of opening the image, resolve where it belongs, open that directory and move it ONE BY ONE by hand make you tired?

This could help you, just as it helped me!


## 2. Tutorial

### 2.1. Add shortcut

1. Select EDIT mode (Ctrl+E or click on button)
2. Hit the desired shortcut, for example:
    - 'i' for 'images'
    - 'a' for 'anime'
    - 'n' for 'naruto'
3. Hit Enter and select destination directory, for example:
    - '/home/USER/Images/Anime/Naruto'
4. Select SORT mode (Ctrl+R or click on button)
5. Write the sequence, and by writing the last key, the image will be moved to the corresponding destination.

### 2.2. Update path of the existing shortcut

1. Select EDIT mode
2. Just add the same shortcut sequence again and select new path

OR

1. [TBD] Use Edit button beside the shortcut.


## 3. Features

- Select source directory for the gallery to be sorted
- 2 modes - SORT and EDIT
- Create shortcut and set destination directory for it
- Repeat last src-dst move by hitting '.'
- Undo the move
- Temporarily preserve part of the shortcut, so instead of repeating the whole 'ian', you can fix 'ia' and
  then hit just the last part of the sequence: 'n' for naruto, 'd' for deathnote and so on.
- Create a subset of gallery photos: Select Copy mode and just copy some photos to target directory, for example to
  show just subset of photos to your family.


## 4. How to build the app

### 4.1. Linux

1. xyz

    ```

    ```

### 4.2. Windows

1.  x

    ```

    ```

## 5. Known issues:

- Videos on Windows are playing, but are not shown in the player. Missing codecs/driver?


## 6. Dependencies

```
sudo dnf install
python3-pip
python3-qt5
```

pip3 install -r requirements.txt
