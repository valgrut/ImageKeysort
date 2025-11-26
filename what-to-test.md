# what-to-test

- move file to dst dir (then check that image in dst exists, image in src does not)
- move file to dst dir, where the file with the same name exist -> should not be moved
- move and then undo move
- move and repeat last operation (dot .)
- copy
- add shortcut on L1
- add shortcut 1 under L1
- add shortcut 2 under L1
- add shortcut on L1
- remove shortcut tree
- remove all shortcuts
- 


# Testovat vnejsi chovani nezavisle na vnitrni strukture, metodach ...
- use pytest-qt!!!! to test the app as end2end. Napr:

1. set edit mode - ctrl + E
2. provides some input in form of some keychars to add shortcut - fc <enter>
3. provide dst path to the dialog and save shortcut
4. open gallery
5. press fc to move current image into dst directory
6. check, that dst directory contains such image.