import sys
import pathlib
from src.Styles import Styles
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication
from src.MainWindow import MainWindow

# Features DONE:
# - [x] Pridat nekam, jaka src slozka je aktualne nastavena
# - [x] Pridat zobrazeni i 3. vnoreni zkratek
# - [x] Pridat counter (x/y), kolik obrazku zbyva v src slozce
# - [x] pridat kontrolu, ktere klavesy lze zmacknout (zablokovat napr. mezernik a bile znaky)
# - [x] Pridat Copy mode, aby se obrazek nepresunul, ale jen zkopiroval do dst.
# - [x] Delete current image (Presune se do slozky TO_DELETE, kde si to pak uzivatel bude moct rucne smazat - to aby porad fungovala funkce Undo - nevim, jak bych to dostaval z kose).
# - [x] Rozsirit Status bar na 2 radky.
# - [x] Pridat moznost zvolit file se shortcuts pro nacteni, a pri ukladani tez.
# - [x] Pridat, ze cudlik bude polopruhledny a po najeti se zviditelni.
# - [x] Pridat obrazky pro buttons (kos s cervenym backgroundem, a takoveto pero pro edit)
# - [x] Kdyz neni otevrena zadna src slozka, tak moct kliknout na plochu, kde byvaji obrazky, pro otevreni dialogu vyberu src slozky.
# - [x] Pridat filtr ze se nactou do galerie pouze .png, .jpeg, .jpg, .gif, proste jen obrazkove formaty. Zadna pdf a tak.
# - [x] Pridat obrazek do imagewidgetu, kdyz neni nactena zadna src slozka.
# - [x] Fixed: All Images were clickable instead of just the one when gallery is empty.
# - [x] Kdyz v galerii dojdou obrazky, vratit tam ten obrazek EmptyInbox.
# - [x] Track changes in shortcuts and ask for saving if changes were made.
# - [x] Pri nacteni shortcuts-dat ulozit cestu, odkud byla vzata a nabidnout ji pak kdyz chci ulozit zmeny.
# - [x] Po najeti na tlacitka/klikatelne veci, se zmeni kurzor na ruku.
# - [x] Zprovoznit ikonu aplikace
# - [x] FIX: searching longest path!
# - [x] Next/Prev buttons, counter a src a image name se zobrazi jen, kdyz je nactena galerie.
# - [x] Edit mode: Pridat moznost odstranit nejakou zkratku, podzkratku ... (o-a = 'o' 'minus' 'a') odstrani zkratku 'a' z rodicovske 'o'.
# - [x] Prerusit to vetveni x.y.z.f() mezi main.GalleryManager.MediaContainerWidget.f() [Jak to delat lepe, nez ze udelat retezec funkci?]
# - [x] Fix focus, abych mohl pouzivat sipky pro prochazeni obrazku.
# - [x] Pridat cudliky na Jump to start of the gallery a na Jump to end of gallery. Dat je vedle Previous a Next image.
# - [x] Add error message, if the directory does not exist, for which we HIT the shortcut (is in shortcut, but does nto exist on disk)
# - [x] Fix: HIT is detected even for sequences containing intermediate nonexisting keys: fxxxxk, oxa, ...
# - [x] Empty the shortcuts (or just update the preview?) if HIT && target dir does not exist physically.
# - [x] Resize image in label to fill the label while keeping ratio and even during the window resizing.
# - [x~] Pridat nekam indikator, jestli jsou provedeny zmeny, nebo ne. (Obvykle je nekde treba '*').
# - [x] Fix crash, when manipulating image, which is removed outside of program, while source directory is loaded.
#   - Kontext: Odstranim/presunu rucne obrazek ve slozce, ktera je otevrena v programu. Kdyz na obrazek (ktery v poli ale porad existuje) sipkama dojdu a zkusim ho odstranit, program crashne.
#   - [x] Pridat file exist check pri manipulaci s obrazkem (pri mv, copy, del) !!!! If does not exist, remove from list.
# - [x] CHECK: co kdyz presunu do dst picture s nazvem Xyz, ale obrazek s timto nazvem jiz ve slozce je? Neprepise se doufam...
# - [x] Pridat klavesovou zkratku pro Na konec a Na zacatek - home a end klavesy.
# - [x] VideoWidget: spravit avi, zprovoznit mp4, nextImage stopne video if current is video, prev to same.
# - [x] Pridat moznost zobrazovat i gify (videoWidget misto imageWidgetu)
# - [x] ! Zmenit border color okna s obrazkama, kdyz je aktivni COPY mode, aby to bylo jasnejsi (uz jsem na nej parkrat zapomenul, ze je aktivni).
# - [x] Vyresit cekani na zkratku, kdyz x, aj xy obsahuje cestu. Kdyz chci poslat img do 'x', nic se nedeje, bo y obsahuje cestu taky. Mozna Timer nebo treba >>>mezernik<<< jako potvrzeni. !!!!!!
# - [x] zmacknutim mezerniku (if Sort mode AND pokud neni namacknuta zadna zkratka), otevre okno s vyberem slozky, kam jednorazove poslat aktualni obrazek.
# - [x] Kdyz pridavam zkratku pod nejakou jinou, nabidnout primarne cestu v rodicovske zkratce (napr. fotky->akce, nova: fotky->narozky, formular zobrazi adresar Fotky jako vychozi)
# - [NE] WONT_DO Pridat i nektere znaky jako labely ($, ...)
# - [X] Pridat CLI argumenty pro spusteni aplikace s preddefinovanymi parametry (napr. --src-dir, --dst-dir, --load-data, --save-data, ...)
# - [X] How many columns of shortcuts to show (1-5) [Settings]
# - [X] Settings saving and loading.
#   - [X] Settings - na jake misto soubor hodit? Kam se divat defaultne? Win vs Linux (~/).
# - [X] Settings - ovladani hlasitosti - mute by default.
# - [X] Tridit zkratky abecedne? (Mozna settings option?)


# Top priority:
# - [ ] !!!! Otestovat cisla a velka pismena jako shortcuts !!!!!!!!
# - [~] !!! Vypisuje se jen N urovni zkratek, nejak ale oznacit, jsou-li tam jeste dalsi. (proto sekvence treba neHITla, bo se tam skryvaly dalsi).
# - [ ] Prochazet TODO v souborech a udelat je.
# - [~] ! Napsat unit testy !!
# - [ ] !!!!! By clicking to image name OR by pressing some shortcut (which?) - rename the file to given string. (!!! Check that new name does not exist in this directory)
# - [ ] Fix videos on Windows
# - [ ] Pridat Type hints ( -> int, myvar: str, ...)
# - [ ] Fix Ctrl+O to open new source directory
# - [ ] Fix, kdyz se prehrava video a zmenim slozku ci jdu dal, video je porad slyset !!!


# Settings:
# - [~] ! Pridat Settings - (v Edit mode): pujde zaskrtnout, jestli povolit pridavani zkratek bez vybrane cesty. !!! To je napad!
# - [~] ! v Edit mode: Pridat varovani, kdyz uz zkratka existuje, a my ji chceme prepsat dst path. (Vyskoci dialog okno ze uz existuje, jestli ji chceme prepsat.) - pridat option do settings, jestli povolit prepsani nebo ne. nebo jestli zobrazit potvrzeni prepsani, nebo prepsat bez potvrzeni.
# - [ ] Settings: Moznost sort podle dst_path, ne podle Key_char.


# Important features TODO:
# - [~] ! REFACTORING
#   - [ ] !!!!!!!!!! Mozna GalleryManager nemit jako Widget a dat tam primo MediaContainerWidget. GalleryManager mit jako ShortcutManager bokem.
# - [~] Tridit zkratky abecedne? (Mozna settings option?)
# - [ ] ! Fix reskalovani toho Shortuc panelu - obcas se zmensuje a zvetsuje dle zobrazeneho obrazku.
# - [ ] ! FIX: Kdyz se pri tvorbe nove zkratky nevybere zadna cesta, tak zkratku nepridavat.! Aktualne se prida prazdna. Nebo dialog okno esi fakt pridat. [??SETTINGS]
# - [ ] Zobrazit historii v History Label kde bude historie zmacknutych zkratek ('afg', ...), aby clovek videl, co se stane, kdyz zmackne '.' (Repeat). Mozna ji pridat POD aktualne mackanou zkratku, sedou barvou.
# - [ ] Zobrazit nazev nactenych dat (soubor se zkratkama) (Nad Nazvama sloupcu by mohl byt label, kde bude zobrazen nazev nacteneho souboru se shortcuts-daty.)
# - [~] ! Pridat varovani, kdyz uz zkratka existuje, a my ji chceme prepsat dst path. (Vyskoci dialog okno ze uz existuje, jestli ji chceme prepsat.)
# - [ ] !!!!! Moznost prejmenovat obrazek - udelat textfield z labelu pro imagename.
# - [ ] Moznost napsat, na kolikaty obrazek se chceme presunout - udelat textfield z image counter labelu. (bude fungovat podobne jako prejmenovani obrazku)
# - [x] Pridat moznost pouzivat backspace, abych mohl odmazat znak ze psane zkratky??
# - [ ] Mezi obrazek a treeview dat vertikalni listu, ktera bude hybatelna - pujde menit pomer mezi sirkou treeViewWidget a image.
# - [ ] !!! Kdyz zmacknu treba 'f'+ mezernik, jednorazove otevrit dialog, kde bude prednastavena dst pro 'f'.
# - [ ] Pridat feedback ohledne prevodu obrazku na text, treba hned po kliknuti zobrazit nacitani, ktere se prerusi po te, co proces prevodu dobehne. Tez mozna pouzit cache a ulozit tan prevedeny text, aby se to neprevadelo furt dokola. Misto kliknuti na obrazek mozna pridat tlacitko.
# - [ ] Mozna nejakou animaci, ze blikne statusbar, kdyz se tam objevi nova zprava, nebo pridat datum a cas zpravy, aby bylo jasne, ze aktualni zprava se tyka treba posledni operace.
# - [ ] TODO: Translate all done tasks and translate todo ideas to EN:
# - [ ] Zmenit barvy pozadi v menu !
# - [ ] Vsude u user-defined strings pridat tr(). Viz: The tr() call around the literal string marks the string for translation. It is a good habit to call tr() on all user-visible strings, in case you later decide to translate your application to other languages. The Internationalization with Qt overview covers tr() in more detail.
# - [~] !!!!! Clicking on the image (**or pressing some shortcut, for example '~' or something**, will convert text on the current image and copy it to clipboard to copy for example to markdown and such.
#       - [ ] Pridat tlacitko pro tohle. Udelat toolbar, kam tohle tlacitko pujde (a asi i dalsi tlacitka)
# - [ ] !!! Presunout veskere styly do app-styles.scss a separovat layoutovani do buildUI() method.
# - [ ] Add do Settings: Otevrit presets z minula
# - [ ] About - tu cast se shortcuts - kam ji presunout? V tom About je to moc velke. Nechat tam jen popis programu.


# Installation, Building
# - [ ] Zacit to normalne buildit vsude jednotne, aby se pouzivaly Resources (ikony a pod) (Makefile1)
# - [ ] Zakomponovat qtsass (pip3 install qtsass --break-system-packages)
#   - [ ] `qtsass src/styles/app-styles.scss -o src/styles/app-styles.qss`
# - [ ] Do kontext menu na Windows (prave kliknuti) ve slozce pridat moznost otevrit ji jako src v Image Keysort.
#   - [ ] Do instalace pridat spusteni registr scriptuu (add-image-keysort.reg), ktery to prida do toho kontext menu.


# Design:
# - [~] Implementovat jednoduchy light a dark mode + option do nastaveni.


# To Fix:
# - [x] Crashing when moving the .git bcz process (medium) is used or what...
# - [ ] ??! Fix error state: 1.) add 'hd' without chosing path. 2.) remove 'd': 'h-d'. 3.) add 'hd'. 4.) issue - empty shortcut on L1 .....CANNOT REPRODUCE NOW.....
# - [x] r -> cesta. c-f -> cesta -> crash !!! Fix.Parents path: Get path for shortcut:  cf c -> Key c -> DEBUG: such sequence does not exist.
# - [ ] !!! Backspace funguje divne, kdyz pouziju + (zarazku) v delsich zkratkach


# Shortcuts management, Shortcut Tree (GUI):
# - [ ] Shortcuts by mely byt scrollovatelne i v Sort modu!
# - [ ] Sort shortcuts alphabetically (a, A, c, G, x) and option2 sort target directories alphabetically. [Settings]!
# - [ ] CustomTreeWidget: 1. Jak zvolit, kolik ma zobrazit sloupcu?? 2. Jak prizpusobit sirku - na zaklade poctu zobrazenych sloupcu? [SETTINGS]
# - [~] Edit/Delete buttons v Tree se zobrazi pouze v Edit modu.
# - [ ] Deriv subclass of treeitem kterej bude obsahovat cudly na remove a edit a dalsi specialni obsahujici pouze cudl Add naspod kazde kategorie a podkategorie.
# - [ ] Udelat CustomTree resizable pomoci QSplitter
# - [~] Klikatko pro pridani a odstraneni zkratky / podzkratky
# - [ ] Po najeti na zkracenou cestu (napr. Images, Naruto, ...) se okamzite zobrazi cela cesta (v bubline).
# - [ ] SORT mode: mit moznost normalne klikat na ta jednotliva pole ve strome, a tam se pri kliknuti obrazek presune.
# - [ ] Pridat zvyraznovani aktualne namacknute zkratky a filtraci - zustane pouze ta a jeji podzkratky.
# - [ ] Pod posledni prvek kazde sekce udelat tenkou caru jako oddelovac. (Nebo nad kazdou hlavni, bo to je root tak by to bylo jednodussi).
# - [ ] Pridat moznost otevrit slozku pri kliknuti na shortcut (Tohle funguje!!!):
#           webbrowser.open(self.shortcutManager.srcPathOfLoadedData)
# - [ ] Moznost rucne pretahovat zkratky pod jine. a pretahovanim je zanorovat pod jine... Nutno pak pridat ruzne checky, ze esi tahle kombinace treba uz neexistuje.
# - [ ] Nejak mit moznost zmenit key_char bez toho, abych musel pridat novy a odstranit predchozi. (treba neco jako "abx/abc" - nahradi x za c)
# - [ ] Settings: Moznost sort podle dst_path, ne podle Key_char.


# Minor issues, future features:
# - [ ] Otevrit a tridit remote slozku - napr. Google Drive a pod ?
# - [ ] Stabni kultura - vse prepsat z var_xyz() na varXyz()
# - [ ] Pridat radu do helpu: Namapovat co nejvic zkratek pod prsty leve ruky (a, e, d, ...)
# - [ ] Pridat radu do helpu: Udelat si mensi shortcuts pro konkretni slozky jako Gaming, a pod.
# - [ ] Vyresit ? pomale nacitani velkych obrazku (6MB+)
# - [~] Separatni repozitar, hodit na reddit, na RH, kolegum,
# - [ ] Pridat slovo "EMPTY" do Inbox obrazku
# - [ ] udelat ikonu pro aplikaci: ikonka obrazek a na ni dat "axc" (Neco jako tam je ted, ale dopsat napis??)
# - [~] Dodelat progress widget
# - [ ] MAYBE: Pridat AI advices based on keywords on image.
# - [ ] Po dotrideni inboxu zobrazit tabulku s gratulaci, treba poctem setridenych obrazku, mozna animace famfar.
# - [ ] Ctrl+F Otevre search bar, a kdyz zadam cast nejake slozky, zobrazi se matchnute slozky s jejich zkratkami. (hlavne kdyz se preset rozroste, tak to muze byt uzitecne)
# - [ ] Jazykova podpora ?
# - [ ] Tooltips


# GIT README.md
# - pridat tam, ze vyhoda je, ze tridime pouze 1 photo at a time! No distraction. No paralysis.



def main():
    QCoreApplication.setOrganizationName("JP")
    QCoreApplication.setOrganizationDomain("wogon.cz")
    QCoreApplication.setApplicationName("Image Keysort")
    from PyQt5.QtGui import QPalette, QColor
    app = QApplication(sys.argv)
    # app.setStyleSheet(pathlib.Path('static/app-styles.qss').read_text())
    defaultPalette = QPalette()
    defaultPalette.setColor(QPalette.Background, QColor("red"))
    app.setPalette(defaultPalette)
    app.setStyleSheet(pathlib.Path('static/app-styles.scss').read_text())
    # app.setStyleSheet(f"""
    #     QWidget {{
    #         background-color: {Styles.mainBackground};
    #     }}
    # """)
    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(window.shortcutManager.askSaveIfChanged)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

