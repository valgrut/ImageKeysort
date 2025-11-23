from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


class Styles:
    mainBackground = "rgb(122, 120, 120)"
    widgetsBgColor = "rgb(191, 189, 189)"
    widgetBorderRadius = 10  # px

    buttonBgColor = widgetsBgColor
    buttonHoverBgColor = "rgb(252, 186, 119)"
    buttonBorderRadius = 5  # px
    buttonActivatedBgColor = "orange"

    shadowEffectOffset = (3, 3)
    shadowEffectBlurRadius = 10

    THEME_DARK = {
        "button_bg": "#335480",
        "button_bg_hover": "#465f80",
        "button_bg_active": "#2b4060",
        "button_border": "#9ba5c7",
    }

    @staticmethod
    def getShadowEffect():
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setOffset(3, 3)
        shadowEffect.setBlurRadius(10)
        return shadowEffect

    @staticmethod
    def get_default_palette():
        pal = QPalette()

        # new:
        pal.setColor(QPalette.Window,     QColor("#7a7878"))  # main-background
        pal.setColor(QPalette.Background, QColor("#bfbdbd"))  # widget-background-color
        pal.setColor(QPalette.Button,     QColor("#bfbdbd"))  # button-background-color
        pal.setColor(QPalette.Highlight,  QColor("#fcba77"))  # button-background-hover-color
        pal.setColor(QPalette.Base,     QColor("#ffa200"))  # button-background-active-color
        pal.setColor(QPalette.Link, QColor("#000000"))  # button-border-color

        # old:
        #
        # pal.setColor(QPalette.WindowText, QColor("#e6e6e6"))
        #
        # pal.setColor(QPalette.Base, QColor("#121212"))
        # pal.setColor(QPalette.AlternateBase, QColor("#1e1f22"))
        # pal.setColor(QPalette.Text, QColor("#e6e6e6"))
        #
        # pal.setColor(QPalette.Button, QColor("#2b2d31"))
        # pal.setColor(QPalette.ButtonText, QColor("#ffffff"))
        #
        # pal.setColor(QPalette.Mid, QColor("#3a3d41"))
        # pal.setColor(QPalette.Dark, QColor("#181a1f"))
        # pal.setColor(QPalette.Light, QColor("#3a3d41"))
        #
        # pal.setColor(QPalette.Highlight, QColor("#ff8c00"))
        # pal.setColor(QPalette.HighlightedText, QColor("#000000"))

        # app.setPalette(pal)
        return pal


    @staticmethod
    def get_dark_palette():
        pal = QPalette()

        # new:
        pal.setColor(QPalette.Window,     QColor("#233f66"))  # main-background
        pal.setColor(QPalette.Background, QColor("#233f66"))
        pal.setColor(QPalette.Button,     QColor("#335480"))  # button-background-color
        pal.setColor(QPalette.Highlight,  QColor("#465f80"))  # button-background-hover-color
        pal.setColor(QPalette.Base,     QColor("#465f80"))  # button-background-active-color
        pal.setColor(QPalette.Link, QColor("#9ba5c7"))  # button-border-color

        # Old:
        # pal.setColor(QPalette.Window, QColor("#1e1f22"))
        # pal.setColor(QPalette.WindowText, QColor("#e6e6e6"))
        #
        # pal.setColor(QPalette.Base, QColor("#121212"))
        # pal.setColor(QPalette.AlternateBase, QColor("#1e1f22"))
        # pal.setColor(QPalette.Text, QColor("#e6e6e6"))
        #
        # pal.setColor(QPalette.Button, QColor("#2b2d31"))
        # pal.setColor(QPalette.ButtonText, QColor("#ffffff"))
        #
        # pal.setColor(QPalette.Mid, QColor("#3a3d41"))
        # pal.setColor(QPalette.Dark, QColor("#181a1f"))
        # pal.setColor(QPalette.Light, QColor("#3a3d41"))
        #
        # pal.setColor(QPalette.Highlight, QColor("#ff8c00"))
        # pal.setColor(QPalette.HighlightedText, QColor("#000000"))

        return pal

    @staticmethod
    def get_light_palette():
        pal = QPalette()

        # new:
        pal.setColor(QPalette.Background, QColor(250, 250, 250))

        # old:
        # pal.setColor(QPalette.Window, QColor("#f2f2f2"))
        # pal.setColor(QPalette.WindowText, QColor("#202020"))
        #
        # pal.setColor(QPalette.Base, QColor("#ffffff"))
        # pal.setColor(QPalette.AlternateBase, QColor("#f2f2f2"))
        # pal.setColor(QPalette.Text, QColor("#202020"))
        #
        # pal.setColor(QPalette.Button, QColor("#e0e0e0"))
        # pal.setColor(QPalette.ButtonText, QColor("#202020"))
        #
        # pal.setColor(QPalette.Mid, QColor("#c0c0c0"))
        # pal.setColor(QPalette.Dark, QColor("#a0a0a0"))
        # pal.setColor(QPalette.Light, QColor("#ffffff"))
        #
        # pal.setColor(QPalette.Highlight, QColor("#2979ff"))
        # pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))

        return pal

