from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


class Styles:
    # mainBackground = "rgb(122, 120, 120)"
    # widgetsBgColor = "rgb(191, 189, 189)"
    # widgetBorderRadius = 10  # px

    # buttonBgColor = widgetsBgColor
    # buttonHoverBgColor = "rgb(252, 186, 119)"
    # buttonBorderRadius = 5  # px
    # buttonActivatedBgColor = "orange"

    shadowEffectOffset = (3, 3)
    shadowEffectBlurRadius = 10

    @staticmethod
    def getShadowEffect():
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setOffset(3, 3)
        shadowEffect.setBlurRadius(10)
        return shadowEffect

    @staticmethod
    def get_retro_palette():
        pal = QPalette()

        pal.setColor(QPalette.Window, QColor("#7a7878"))  # main window bg
        pal.setColor(QPalette.WindowText, QColor("#000000"))  # text on Window

        # item-view content area
        pal.setColor(QPalette.Base, QColor("#bfbdbd"))  # tree/list/table bg
        pal.setColor(QPalette.AlternateBase, QColor("#d0cece"))
        pal.setColor(QPalette.Text, QColor("#000000"))  # text in item-views

        # buttons
        pal.setColor(QPalette.Button, QColor("#bfbdbd"))
        pal.setColor(QPalette.ButtonText, QColor("#000000"))

        # lines/borders and shades
        pal.setColor(QPalette.Mid, QColor("#000000"))
        pal.setColor(QPalette.Link, QColor("#000000"))  #000000 # “border” color

        # selection
        pal.setColor(QPalette.Highlight, QColor("#fcba77"))
        pal.setColor(QPalette.HighlightedText, QColor("#ffa200"))

        return pal


    @staticmethod
    def get_dark_palette():
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor("#233f66"))  # main window bg
        pal.setColor(QPalette.WindowText, QColor("#000000"))  # text on Window

        # item-view content area
        pal.setColor(QPalette.Base, QColor("#335480"))  # tree/list/table bg
        pal.setColor(QPalette.AlternateBase, QColor("#d0cece"))
        pal.setColor(QPalette.Text, QColor("#000000"))  # text in item-views

        # buttons
        pal.setColor(QPalette.Button, QColor("#335480"))
        pal.setColor(QPalette.ButtonText, QColor("#000000"))

        # lines/borders and shades
        pal.setColor(QPalette.Mid, QColor("#000000"))
        pal.setColor(QPalette.Link, QColor("#9ba5c7"))  # “border” color

        # selection
        pal.setColor(QPalette.Highlight, QColor("#fcba77"))
        pal.setColor(QPalette.HighlightedText, QColor("#ffa200"))
        return pal


    @staticmethod
    def get_night_palette():
        pal = QPalette()
        
        # --- Window / general surfaces ---
        pal.setColor(QPalette.Window,          QColor("#111318"))  # app background
        pal.setColor(QPalette.WindowText,      QColor("#e5e7eb"))  # text on window

        # --- Item/view surfaces (lists, trees, tables, inputs) ---
        pal.setColor(QPalette.Base,            QColor("#171a20"))  # content surface
        pal.setColor(QPalette.AlternateBase,   QColor("#1c2027"))  # zebra rows
        pal.setColor(QPalette.Text,            QColor("#f3f4f6"))  # primary content text

        # --- Buttons ---
        pal.setColor(QPalette.Button,          QColor("#1e2230"))  # button surface
        pal.setColor(QPalette.ButtonText,      QColor("#e5e7eb"))  # button text

        # --- Borders / lines / shades ---
        pal.setColor(QPalette.Light,           QColor("#32384a"))  # top highlights
        pal.setColor(QPalette.Midlight,        QColor("#2b3040"))
        pal.setColor(QPalette.Mid,             QColor("#252a38"))  # standard border
        pal.setColor(QPalette.Dark,            QColor("#0c0f15"))
        pal.setColor(QPalette.Shadow,          QColor("#000000"))

        # --- Selection / active states (accent) ---
        pal.setColor(QPalette.Highlight,       QColor("#ff8c00"))  # accent (orange)
        pal.setColor(QPalette.HighlightedText, QColor("#000000"))  # readable on orange

        # --- Links (your request) ---
        pal.setColor(QPalette.Link,            QColor("#9ba5c7"))
        pal.setColor(QPalette.LinkVisited,     QColor("#8a94b8"))

        # --- Tooltips ---
        pal.setColor(QPalette.ToolTipBase,     QColor("#1f2431"))
        pal.setColor(QPalette.ToolTipText,     QColor("#e5e7eb"))

        return pal

    @staticmethod
    def get_light_palette():
        pal = QPalette()

        # --- Window / general surfaces ---
        pal.setColor(QPalette.Window, QColor("#f5f6f8"))  # app background
        pal.setColor(QPalette.WindowText, QColor("#1f2937"))  # text on window

        # --- Item/view surfaces (lists, trees, tables, inputs) ---
        pal.setColor(QPalette.Base, QColor("#ffffff"))  # content surface
        pal.setColor(QPalette.AlternateBase, QColor("#f8fafc"))  # zebra rows
        pal.setColor(QPalette.Text, QColor("#111827"))  # primary content text

        # --- Buttons ---
        pal.setColor(QPalette.Button, QColor("#f3f4f6"))  # button surface
        pal.setColor(QPalette.ButtonText, QColor("#1f2937"))  # button text

        # --- Borders / lines / shades ---
        pal.setColor(QPalette.Light, QColor("#ffffff"))  # top highlights
        pal.setColor(QPalette.Midlight, QColor("#e5e7eb"))
        pal.setColor(QPalette.Mid, QColor("#d1d5db"))  # standard border
        pal.setColor(QPalette.Dark, QColor("#9ca3af"))
        pal.setColor(QPalette.Shadow, QColor("#6b7280"))

        # --- Selection / active states (accent) ---
        pal.setColor(QPalette.Highlight, QColor("#ff8c00"))  # accent (orange)
        pal.setColor(QPalette.HighlightedText, QColor("#000000"))

        # --- Links ---
        pal.setColor(QPalette.Link, QColor("#2563eb"))
        pal.setColor(QPalette.LinkVisited, QColor("#1e40af"))

        # --- Tooltips ---
        pal.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
        pal.setColor(QPalette.ToolTipText, QColor("#111827"))

        return pal

