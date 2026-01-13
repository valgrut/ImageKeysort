import argparse
import sys
import pathlib
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication
from src.MainWindow import MainWindow

"""
Features DONE:
- [x] Pridat nekam, jaka src slozka je aktualne nastavena
- [x] Pridat zobrazeni i 3. vnoreni zkratek
- [x] Pridat counter (x/y), kolik obrazku zbyva v src slozce
- [x] pridat kontrolu, ktere klavesy lze zmacknout (zablokovat napr. mezernik a bile znaky)
- [x] Pridat Copy mode, aby se obrazek nepresunul, ale jen zkopiroval do dst.
- [x] Delete current image (Presune se do slozky TO_DELETE, kde si to pak uzivatel bude moct rucne smazat - to aby porad fungovala funkce Undo - nevim, jak bych to dostaval z kose).
- [x] Rozsirit Status bar na 2 radky.
- [x] Pridat moznost zvolit file se shortcuts pro nacteni, a pri ukladani tez.
- [x] Pridat, ze cudlik bude polopruhledny a po najeti se zviditelni.
- [x] Pridat obrazky pro buttons (kos s cervenym backgroundem, a takoveto pero pro edit)
- [x] Kdyz neni otevrena zadna src slozka, tak moct kliknout na plochu, kde byvaji obrazky, pro otevreni dialogu vyberu src slozky.
- [x] Pridat filtr ze se nactou do galerie pouze .png, .jpeg, .jpg, .gif, proste jen obrazkove formaty. Zadna pdf a tak.
- [x] Pridat obrazek do imagewidgetu, kdyz neni nactena zadna src slozka.
- [x] Fixed: All Images were clickable instead of just the one when gallery is empty.
- [x] Kdyz v galerii dojdou obrazky, vratit tam ten obrazek EmptyInbox.
- [x] Track changes in shortcuts and ask for saving if changes were made.
- [x] Pri nacteni shortcuts-dat ulozit cestu, odkud byla vzata a nabidnout ji pak kdyz chci ulozit zmeny.
- [x] Po najeti na tlacitka/klikatelne veci, se zmeni kurzor na ruku.
- [x] Zprovoznit ikonu aplikace
- [x] FIX: searching longest path!
- [x] Next/Prev buttons, counter a src a image name se zobrazi jen, kdyz je nactena galerie.
- [x] Edit mode: Pridat moznost odstranit nejakou zkratku, podzkratku ... (o-a = 'o' 'minus' 'a') odstrani zkratku 'a' z rodicovske 'o'.
- [x] Prerusit to vetveni x.y.z.f() mezi main.GalleryManager.MediaContainerWidget.f() [Jak to delat lepe, nez ze udelat retezec funkci?]
- [x] Fix focus, abych mohl pouzivat sipky pro prochazeni obrazku.
- [x] Pridat cudliky na Jump to start of the gallery a na Jump to end of gallery. Dat je vedle Previous a Next image.
- [x] Add error message, if the directory does not exist, for which we HIT the shortcut (is in shortcut, but does nto exist on disk)
- [x] Fix: HIT is detected even for sequences containing intermediate nonexisting keys: fxxxxk, oxa, ...
- [x] Empty the shortcuts (or just update the preview?) if HIT && target dir does not exist physically.
- [x] Resize image in label to fill the label while keeping ratio and even during the window resizing.
- [x] Pridat nekam indikator, jestli jsou provedeny zmeny, nebo ne. (Obvykle je nekde treba '*').
- [x] Fix crash, when manipulating image, which is removed outside of program, while source directory is loaded.
  - Kontext: Odstranim/presunu rucne obrazek ve slozce, ktera je otevrena v programu. Kdyz na obrazek (ktery v poli ale porad existuje) sipkama dojdu a zkusim ho odstranit, program crashne.
  - [x] Pridat file exist check pri manipulaci s obrazkem (pri mv, copy, del) !!!! If does not exist, remove from list.
- [x] CHECK: co kdyz presunu do dst picture s nazvem Xyz, ale obrazek s timto nazvem jiz ve slozce je? Neprepise se doufam...
- [x] Pridat klavesovou zkratku pro Na konec a Na zacatek - home a end klavesy.
- [x] VideoWidget: spravit avi, zprovoznit mp4, nextImage stopne video if current is video, prev to same.
- [x] Pridat moznost zobrazovat i gify (videoWidget misto imageWidgetu)
- [x] ! Zmenit border color okna s obrazkama, kdyz je aktivni COPY mode, aby to bylo jasnejsi (uz jsem na nej parkrat zapomenul, ze je aktivni).
- [x] Vyresit cekani na zkratku, kdyz x, aj xy obsahuje cestu. Kdyz chci poslat img do 'x', nic se nedeje, bo y obsahuje cestu taky. Mozna Timer nebo treba >>>mezernik<<< jako potvrzeni. !!!!!!
- [x] zmacknutim mezerniku (if Sort mode AND pokud neni namacknuta zadna zkratka), otevre okno s vyberem slozky, kam jednorazove poslat aktualni obrazek.
- [x] Kdyz pridavam zkratku pod nejakou jinou, nabidnout primarne cestu v rodicovske zkratce (napr. fotky->akce, nova: fotky->narozky, formular zobrazi adresar Fotky jako vychozi)
- [NE] WONT_DO Pridat i nektere znaky jako labely ($, ...)
- [X] Pridat CLI argumenty pro spusteni aplikace s preddefinovanymi parametry (napr. --src-dir, --dst-dir, --load-data, --save-data, ...)
- [X] How many columns of shortcuts to show (1-5) [Settings]
- [x] r -> cesta. c-f -> cesta -> crash !!! Fix.Parents path: Get path for shortcut:  cf c -> Key c -> DEBUG: such sequence does not exist.
- [X] Settings saving and loading.
  - [X] Settings - na jake misto soubor hodit? Kam se divat defaultne? Win vs Linux (~/).
- [X] Settings - ovladani hlasitosti - mute by default.
- [X] Tridit zkratky abecedne? (Mozna settings option?)
- [x] Pridat moznost pouzivat backspace, abych mohl odmazat znak ze psane zkratky??
- [X] !!!!! Clicking on the image (**or pressing some shortcut, for example '~' or something**, will convert text on the current image and copy it to clipboard to copy for example to markdown and such.
      - [X] Pridat tlacitko pro tohle. Udelat toolbar, kam tohle tlacitko pujde (a asi i dalsi tlacitka)
- [X] Presunout veskere styly do app-styles.scss
- [X] kdyz se tam objevi nova zprava, nebo pridat datum a cas zpravy, aby bylo jasne, ze aktualni zprava se tyka treba posledni operace.
- [X] About - tu cast se shortcuts - kam ji presunout? V tom About je to moc velke. Nechat tam jen popis programu. (Inspirovat se treba Pycharm, jak to je udelane tam)
- [X] Pridat moznost undo copy operation. Kdyz se clovek splete, tak lze undo i copy operaci, takze se proste z dst ta fotka smaze.
- [X] Fix: ClearTree -> SaveChanges? Kdyz nevyberu zadnou slozku, stejne se to smaze. Takze pokracovat k akci jen, kdyz se fakt zvoli soubor do ktereho ulozit zkratky.
- [X] Settings - (v Edit mode): pujde zaskrtnout, jestli povolit pridavani zkratek bez vybrane cesty. Default povoleno.
- [X] Settings: v Edit mode: Pridat varovani, kdyz uz zkratka existuje, a my ji chceme prepsat dst path. (Vyskoci dialog okno ze uz existuje, jestli ji chceme prepsat.) - pridat option do settings, jestli povolit prepsani nebo ne. nebo jestli zobrazit potvrzeni prepsani, nebo prepsat bez potvrzeni.
- [X] Osetrit, kdyz kliknu na extract, ale neni nacteny zadny obrazek.
- [X] Fix reskalovani toho Shortcut panelu - obcas se zmensuje a zvetsuje dle zobrazeneho obrazku.
- [X] Zmena zkratky na jinou - mit moznost zmenit key_char bez toho, abych musel pridat novy a odstranit predchozi. (treba neco jako "abx/abc" - nahradi x za c)
      - [X] Fix edge cases - existuje x, pridame a, zmenime a na x -> zmizi.
      - [X] Prejmenovani neexistujici zkratky
- [X] Implementovat jednoduchy light a dark mode + option do nastaveni.
- [x] Crashing when moving the .gif because process (medium) is used or what...
- [X] vymenit statusBar-label za QStatusBar
- [X] !!! Fix Crash kdyz preklikavam mezi default settings a nasledne menim themes.
- [X] Po refaktoru EditModeHandler po spusteni neni focus na hlavnim widgetu, takze zadne zkratky nefunguji a crashne to aplikaci.
- [X] Pridat do menu kategorii "Pictures nebo Gallery", kde budou veci jako Undo, next image, open gallery, a tak. A "Shortcuts", kde pujde Undo pro shortcut operace - jako undo odstraneni zkratky, pridany zkratky, zmenu cesty a tak.
- [X] Shortcuts by mely byt scrollovatelne i v Sort modu!
- [X] Misto debug print() nahradit za logging module
- [X] Do menu->File pridat: Toggle On Toolbar - on totiz jde vypnout, kdyz se na nej klikne pravym, pak zmizi, a neni moznost ho vratit.
- [X] Fix Ctrl+O to open new source directory
- [X] Reset / Drop all changes in the shortcuts (revert to last saved state) - button vedle ClearTree.
- [X] Drop changes / Clear tree -> Add confirmation dialogue.
- [X] Pokud aktualni soubor neni obrazek, tak disable TextExtraction tlacitko.
- [X] MenuBar -> Shortcuts -> add Clear shortcut tree
- [X] Text file Previewer - pridat kontrolu, jak je textak velky. Pokud vic nez X MB (napr rockyou.txt), nacist pouze y prvnich radku.
- [X] Fix: add 'ac' s dst, pak add dst for 'a'. pak zkusit 'a + mezernik' -> crash. Pricina byla, ze se nekontrolovalo, jestli je vubec nactena nejaka src slozka.
- [X] Zprovoznit a spravit ikonky na Linuxu.
- [X] Pokud aktualni soubor neni obrazek (nebo aj video??), tak disable CropImage tlacitko.
- [X] Kdyz zmacknu treba 'f'+ mezernik, jednorazove otevrit dialog, kde bude prednastavena dst pro 'f'.
- [X] Anonymizovat testovaci data - pro kazdy .py, .md a pod proste jen sebrat neco z netu, neco generickeho. Ne moje scripty!!!
- [X] v edit modu nechat zasednout image cast, aby bylo zretelne ze to neni sort mode...
- [X] !!!!! Sort mode (Copy option): Pridat moznost pred shortcut pridat znak, treba , a ; pro kopirovani bez zapinani copy rezimu (nebo by to mohl zapnout interne pouze docasne a pak vypnout. Jeden znak udela copy a go to next img, druhy pouze copy ale zustane na aktualnim.
- [X] !! Omezit, aby se do aktualne zmacknutych shortcuts v keyLabel nezapisovaly emptyspaces, ctrl a ruzne hovadiny. Jen a-zA-Z0-9.
- [X] Add another keyboard shortcut (F2) to initiate file renaming.
- [X] Kdyz pridam zkratku s prazdnou cestou a chci ji HIT v sort modu, crash!!!!

Links:
    - https://doc.qt.io/archives/qt-5.15/stylesheet-examples.html#customizing-qmenu
    - Manage pytest output: https://docs.pytest.org/en/stable/how-to/output.html

====== Main features to implement ======
- [X] Change names of the files
- [ ] Rework ShortcutTreeView
- [~] Crop image / video (sources: keyboard shortcut, button in menu, button in toolbar)
        - [X] Crop image by mouse click + drag
- [ ] Zoom in/out the image (imageView only)
        - Kvuli velkym obrazkum s textem, ktery je kvuli velikosti uz skoro necitelny.
- [ ] Add tags into the filename
        - [ ] Just for me - define shortcuts (ctrl+1, ctrl+2 ...) a k nim priradit konkretni " [xyz]".
- [ ] Tabs (vice "instanci" v jednom okne, kde kazda instance bude mit svou galerii a shortcuts otevrene.


### Crop - related todo:
- I need to be able to:
      - save cropped image into the source directory via GalleryManager
          - So, move image cropper to the GalleryManager? Then I could use it even for the video cropping.
      - Be able to revert back the cropping (save image before crop internally vs externally to be able to revert back?)
          - Shortcut to revert image cropping and start over
      - Crop a video too.
          - Use ffmpeg app; Will it work on windows too???
- [ ] V1: QRubberBand (simple) nebo V2: QGraphicView (okraje s kruhama v rozich a po stranach)
- [ ] Fix: still small misalignment between cursor's tip position and rubberband.
- [X] Show rubberband to all directions, not just from top left to right down.
        - [ ] Show guide lines (dashed vertical and horizontal from the point of first click to the all way up and all way down) (center vertical/horizontal, thirds, ...), so user can better align the crop area.
- [ ] Undo/Redo: Melo by jit ctrl+z nebo nejaka podobna zkratka, protoze samozrejme to lze podelat nejak. Nekolidovat s undo/redo pro move/copy.
- [ ] REPEAT last crop!!!!!!!! (start + end coords).
- [ ] !!! Use function from Cropper.py class instead of directly in the ImageWidget. !!!
- [ ] Fix: Cannot Undo crop operation on an image that is cropped using repeatCrop().
- [ ] Fix: Add check that the image size of template image is the same as current image size when repeating last crop.

### Zoom - related todo:
- [ ] implement zoom


### Rename - related todo:
- [ ] Undo/Redo


### Text extraction
- [ ] Ukladat do souboru ve slozce extracted/<nazev-obrazku> [extracted].txt
        - [ ] Pred extrahovanim se podivat, jestli tam uz soubor s extrahovanym textem pro tento obrazek neni.


### Tagging (sub-feature pro Rename)
- [ ] Moznost zadefinovat TAGY, ktery se pri rename zobrazi naboku, a kliknutim na nejaky tag se prida do nazvu.
        - Napr.: Tagy: IG, Vertigo, PoledancerXYZ  ->  se do nazvu (pred suffix) pridat treba " [PoledancerXYZ]".
        - [ ] Popremyslet treba nad zkratkama pro treba vyskoceni rolovaci nabidky s tagama, a sipkama a enter pridavat.
            - [ ] Treba Ctrl+T
        - [ ] Edit mode Ctrl+T /klik na menu - Vyskoci popup okno, ktere se otevre v Edit modu pro editaci/pridavani/odebirani.
        - [ ] Tagy by se mohly definovat v popup okne, ktere se otevre v Edit modu pro editaci/pridavani/odebirani
- [ ] Undo/Redo


Important - Misc:
- [ ] !!!! Otestovat cisla a velka pismena jako shortcuts !!!!!!!!
- [~] !!! Vypisuje se jen N urovni zkratek, nejak ale oznacit, jsou-li tam jeste dalsi. (proto sekvence treba neHITla, bo se tam skryvaly dalsi).
  - Udelat metodu, ktera vrati aktualni nejvyssi pocet zanoreni. Porovnat s Settings.getMaxNesting a pokud realny je vetsi nez povoleny, pridat treba ">" do nazvu.
- [ ] Prochazet TODO v souborech a udelat je.
- [~] ! Napsat unit testy !!
- [ ] !!!!!!! Setridit a zorganizovat MainWindow init metodu - vsechny Actions k sobe, vsechny .connect k sobe a tak.
- [ ] Help: Pridat examples - jak vypada tree, jak bude vypadat po pridani
nejake zkratky, jak bude vypadat po odstraneni/presunu/zmene keychar...
- [ ] Add "__DELETED__" string for the trash folder into settings (or at least into variable and use that everywhere instead of hardcoded string)
- [ ] !!! Pridat nahled predchoziho a nasledujiciho obrazku. Hodi se, kdyz chci fotky tridit mega rychle (treba jen 2 kategorie).
- [ ] While left/right arrow is pressed, move images (prevent need to press it tousands of times) - jde to, ale zpomalit malinko.
- [ ] Hide number showing number of images in the source directory.


Settings:
- [ ] Settings: Moznost sort podle dst_path, (krom podle insert order (default) a podle Key_char (alphabetically).
- [ ] Settings: Add option which types of files to allow / show (videos/images/pdfs/text files/ ...)
- [ ] Settings: show/hide gallery counter label (muze nekoho stresovat, kolik toho jeste zbyva v dane slozce setridit.)
- [ ] Pridat do Settings: Otevrit posledni src slozku pri startu aplikace.


Refactoring and code tweaking
- [~] EditModeHandler
- [ ] SortModeHandler !
- [X] ShortcutManager
- [~] Pridat Type hints ( -> int, myvar: str, ...)
- [ ] GalleryManager a MediaContainerWidget - lepsi rozhodovani ohledne zobrazeni (obrazek vs video vs text vs pdf)
- [~] Vytvorit Actions z akci, ktere jeste Action nemaji. Vymenit to za prime volani metod. Zvlast u veci, ktere jsou volane z vice mist (button / shortcut / menu / ...)


Important features TODO:
- [~] Feature: Rename current file. (Details above.)
- [~] Feature: Crop image. (Details above.)
- [ ] Vedle srcDirectoryLabel jeste pridat Button pro otevreni nove slozky. Jinak se musi do menu nebo pouzit ctrl+o, ale chce to i cudlik.
- [ ] Moznost zavrit slozku (Close gallery) pomoci polozky v Gallery menu.
- [ ] Mozna nejakou animaci, nebo ze blikne statusbar, kdyz tam pribude nova informace.
- [ ] Zobrazit nazev nactenych dat (soubor se zkratkama) (Nad Nazvama sloupcu by mohl byt label, kde bude zobrazen nazev nacteneho souboru se shortcuts-daty.) nebo do WindowTitle?
- [ ] Moznost napsat, na kolikaty obrazek se chceme presunout - udelat textfield z image counter labelu. (bude fungovat podobne jako prejmenovani obrazku)
- [ ] Mezi obrazek a treeview dat vertikalni listu, ktera bude hybatelna - pujde menit pomer mezi sirkou treeViewWidget a image.
- [ ] Vsude u user-defined strings pridat tr(). Viz: The tr() call around the literal string marks the string for translation. It is a good habit to call tr() on all user-visible strings, in case you later decide to translate your application to other languages. The Internationalization with Qt overview covers tr() in more detail.
- [ ] !!!! Add do Settings: Otevrit presets z minula
- [ ] Pridat do arguments --debug a jako mozny parametr None (default None kdyz neposkytnut), INFO, WARN, ERROR.
- [ ] !!!! Pridat moznost vratit zpet zmeny v ShortcutTree (nahrazeni dst, operace (/, >, -) a pod).
  - mvHistory presunout do separatni tridy a mit tam metody jako pop(), getLast(), push() a pod. Mozna pouzit QUndoStack, QUndoCommand, ....
- [ ] Support PDF preview - QPdfDocument + QPdfView [Qt6 required]
- [ ] TextPreviewWidget - Add scrolling with up/down arrow keys
- [ ] Mozna pridat zobrazeni metadat doprava (velikost, rozliseni, typ, ...) (pridat i pravou listu); Nebo je zobrazovat nad obrazkem vedle nazvu a tak.
- [ ] Moznost Undo/Redo rename obrazku (proste dalsi undoable operace push do undo stacku) Ale v jakem modu? Ja uplne nechci,aby to kolidovalo s undo move operacemi.
- [ ] Zopakovat posledni copy operaci pomoci ',. a ;.'
- [ ] Delete button do menu a do toolbaru !!!!!
- [ ] Rotate image button (staci 1 smer) do toolbaru. Pozor ale, ty obrazky se obcas zobrazuji jinak, nez jse zobrazuje windows explorer. Proc???
- [ ] !!!!! crop (mouse click/release se bude registrovat pouze, pokud bude aktivni crop mode - aktivni tlacitko Crop.
- [ ] Pridat novou polozku do menu: Tools -> Extract Text ; Crop image ; Rename image ; Undo (ctrl+shift+z) - only those tools operations ; Redo (only those); 
      - Commands deprecation. Napr pro obrazek, ktery prejmenuju a pak presunu, se prejmenovaci command deprecatne ve stacku, protoze obrazek uz bude "vyrizeny".
      - Jeste nevim, jestli pak kdyz obrazek vratim (undo na move), tak se ten rename command reaktivuje, nebo zustane deprecatnuty.

Consider (Maybe):
- [ ] ? mozna: Zobrazit historii v History Label kde bude historie zmacknutych zkratek ('afg', ...), aby clovek videl, co se stane, kdyz zmackne '.' (Repeat). Mozna ji pridat POD aktualne mackanou zkratku, sedou barvou.
- [ ] separovat layoutovani do buildUI() method.
- [ ] textExtraction: zobrazit nacitaci kolecko pri cekani na dokonceni.
- [ ] textExtraction: Tez mozna pouzit cache a ulozit tan prevedeny text, aby se to neprevadelo furt dokola.
- [ ] V MenuBar se inspirovat Pycharm treba - napr Help->(productivity guide, About, Keymap reference, Submit a bug report, ...)


Installation, Building
- [ ] Zacit to normalne buildit vsude jednotne, aby se pouzivaly Resources (ikony a pod) (Makefile1)
- [ ] Zakomponovat qtsass (pip3 install qtsass --break-system-packages)
  - [ ] `qtsass src/styles/app-styles.scss -o src/styles/app-styles.qss`
- [ ] Do kontext menu na Windows (prave kliknuti na slozku nebo ve slozce) pridat moznost otevrit ji jako src v Image Keysort.
  - [ ] Do instalace pridat spusteni registr scriptuu (add-image-keysort.reg), ktery to prida do toho kontext menu.
- [ ] Upgrade from Qt5 to Qt6
- [~] Add ImakeKeysort into Fedora's Files OpenWith. Just like for Windows.
- [~] Add Image Keysort into Fedora's app list (so it appears in the app launcher/search).


Design:
- [ ] Pridat do next/first/previous/last image buttons Ikonku sipky.


To Fix:
- [ ] !!! Fix - Backspace funguje divne, kdyz pouziju + (zarazku) v delsich zkratkach
- [ ] Fix videos on Windows (Codec?)
- [ ] Fix, kdyz se prehrava video a zmenim slozku ci jdu dal, video je porad slyset !!! Pouzit signaly a sloty pro stop.
- [ ] Sentinel set + space key in sort mode. seq: acde; nastavit ac+; acd<mezernik> -> Error zkratka 'd' neexistuje. Mela by se ale pouzit i cast pred sentinelem ('ac').
- [ ] SortMode: abc<enter>cde<enter>xyz<enter> ... vzdy prepisuje predchozi sentinel. Udelat s tim neco nebo to tak nechat?
- [ ] Textove dokumenty nemaji oranzovy ramecek v Copy modu
- [ ] nelze smazat soubor, kdyz uz se v __delete__ takovy nachazi. Hmmm.
- [ ] V EditMode nejde pouzit Esc pro zruseni zmeny jmena souboru. Focus je na psani keySeqa jeho zobrazeni, takze Esc se neregistruje. (V sort funguje spravne)
    - [ ] Mozna v Edit modu zakazat text extraction, renaming a pod. proste vsechno, co neni editace zkratek.
- [ ] !!!!!!! Crash behem cropu tesne po prejmenovani obrazku.
  
    ```
    Full path: /home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/testing-data/downloads/BA-program-2024.jpeg_cropped_small.png
    File without ext: BA-program-2024.jpeg_cropped_small
    Source dir: /home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/testing-data/downloads
    Extension: .png
    File name: BA-program-2024.jpeg_cropped_small.png

    Traceback (most recent call last):
      File "/home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/src/ImageWidget.py", line 234, in mouseReleaseEvent
        shutil.copy2(currentFilePath, pathlib.Path(trashDir, currentFile))
        ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/lib64/python3.13/shutil.py", line 468, in copy2
        copyfile(src, dst, follow_symlinks=follow_symlinks)
        ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/lib64/python3.13/shutil.py", line 260, in copyfile
        with open(src, 'rb') as fsrc:
            ~~~~^^^^^^^^^^^
    FileNotFoundError: [Errno 2] No such file or directory: 
      '/home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/testing-data/downloads/BA-program-2024.jpeg_cropped_small.png'
    ```


Shortcuts management, Shortcut Tree (GUI):
- [ ] Sort shortcuts alphabetically (a, A, c, G, x) [DONE] and option2 sort target directories alphabetically. [Settings]!
- [ ] CustomTreeWidget:  2. Jak prizpusobit sirku - mozna na zaklade poctu zobrazenych sloupcu?
- [~] Edit/Delete buttons v Tree se zobrazi pouze v Edit modu.
- [ ] Deriv subclass of treeitem kterej bude obsahovat cudly na remove a edit a dalsi specialni obsahujici pouze cudl Add naspod kazde kategorie a podkategorie.
- [ ] Udelat CustomTree resizable pomoci QSplitter
- [~] Klikatko pro pridani a odstraneni zkratky / podzkratky
- [ ] Pravym kdyz se klikne na radek ve strome, moznosti - upravit key_char, upravit dst, remove line...
- [ ] Po najeti na zkracenou cestu (napr. Images, Naruto, ...) se okamzite zobrazi cela cesta (v bubline).
- [ ] SORT mode: mit moznost normalne klikat na ta jednotliva pole ve strome, a tam se pri kliknuti obrazek presune.
- [ ] Pridat zvyraznovani aktualne namacknute zkratky a filtraci - zustane pouze ta a jeji podzkratky.
- [ ] Pod posledni prvek kazde sekce udelat tenkou caru jako oddelovac. (Nebo nad kazdou hlavni, bo to je root tak by to bylo jednodussi).
- [ ] Pridat moznost otevrit slozku pri kliknuti na shortcut (Tohle funguje!!!):
          webbrowser.open(self.shortcutManager.srcPathOfLoadedData)
- [ ] Moznost rucne pretahovat zkratky pod jine. a pretahovanim je zanorovat pod jine... Nutno pak pridat ruzne checky, ze esi tahle kombinace treba uz neexistuje.
- [ ] Settings: Moznost sort podle dst_path, ne podle Key_char.
- [ ] Existuje moveToTrash() od Qt, ale nevim, esi ji pouzit.
- [ ] Expand / Collapse everything under a shortcut - by doubleclicking the shortcut?
- [ ] Expand / Collapse all shortcuts - button in Edit mode.
- [ ] Moznost, ze by Napr: "a-" mohla odstranit vsechny podzkratky pod 'a' (a, a.b, a.c.d, ...)
- [ ] Tag / color nodes - Add a color or tag (e.g. game, editing, global) for quick visual scanning.
- [ ] Mozna nekde zobrazovat dynamicky, ktery nasledujici keychar je k dispozici. pak nejaky zmacknu, a vypise to jeho dalsi. Uzitecne pro vetsi presety.


Misc:
- [ ] Naucit se poradne pracovat s Pycharm
- [ ] Naucit se s pdb (python debuggerem)


Minor issues, future features:
- [ ] Translate all done tasks and ideas to EN
- [ ] Otevrit a tridit remote slozku - napr. Google Drive a pod ?
- [ ] Stabni kultura - vse prepsat z var_xyz() na varXyz()
- [ ] Pridat radu do helpu: Namapovat co nejvic zkratek pod prsty leve ruky (a, e, d, ...)
- [ ] Pridat radu do helpu: Udelat si mensi shortcuts pro konkretni slozky jako Gaming, a pod.
- [ ] Vyresit ? pomale nacitani velkych obrazku (6MB+)
- [~] Separatni repozitar, hodit na reddit, na RH, kolegum,
- [ ] Pridat slovo "EMPTY" do Inbox obrazku
- [ ] udelat ikonu pro aplikaci: ikonka obrazek a na ni dat "axc" (Neco jako tam je ted, ale dopsat napis??)
- [ ] Dodelat progress widget
- [ ] MAYBE: Pridat AI advices based on keywords on image.
- [ ] Po dotrideni inboxu zobrazit tabulku s gratulaci, treba poctem setridenych obrazku, mozna animace famfar.
- [ ] Ctrl+F Otevre search bar, a kdyz zadam cast nejake slozky, zobrazi se matchnute slozky s jejich zkratkami. (hlavne kdyz se preset rozroste, tak to muze byt uzitecne)
- [ ] Jazykova podpora ?
- [ ] Tooltips
- [ ] !!! Odkaz na cofee-cofee na dobrovolny prispevek na vyvoj. Viz GPT rada jak to zmonetizovat. Pohledat i web "How to sell SW".
- [ ] Pridat komentare metod a trid (Vygenerovat AI)
- [ ] Pridat treba nejake ADHD notes...


### App description, features, usage
- Quickly rename files
- Quickly add tags into the file names
- Super simple image cropping (e.g. instagram screenshots)

"""


# GIT README.md
# - pridat tam, ze vyhoda je, ze tridime pouze 1 photo at a time! No distraction. No paralysis.
# - jedna z prvnich variant v commitu: c15c6127   (git reset --hard c15c6127)

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

