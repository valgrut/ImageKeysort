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
    
    @staticmethod
    def getShadowEffect():
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setOffset(3, 3)
        shadowEffect.setBlurRadius(10)
        return shadowEffect

    @staticmethod
    def get_default_palette():
        pal = QPalette()

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

        # app.setPalette(pal)
        return pal


    @staticmethod
    def apply_dark_palette(app):
        pal = QPalette()

        pal.setColor(QPalette.Window, QColor("#1e1f22"))
        pal.setColor(QPalette.WindowText, QColor("#e6e6e6"))

        pal.setColor(QPalette.Base, QColor("#121212"))
        pal.setColor(QPalette.AlternateBase, QColor("#1e1f22"))
        pal.setColor(QPalette.Text, QColor("#e6e6e6"))

        pal.setColor(QPalette.Button, QColor("#2b2d31"))
        pal.setColor(QPalette.ButtonText, QColor("#ffffff"))

        pal.setColor(QPalette.Mid, QColor("#3a3d41"))
        pal.setColor(QPalette.Dark, QColor("#181a1f"))
        pal.setColor(QPalette.Light, QColor("#3a3d41"))

        pal.setColor(QPalette.Highlight, QColor("#ff8c00"))
        pal.setColor(QPalette.HighlightedText, QColor("#000000"))

        app.setPalette(pal)

    @staticmethod
    def apply_light_palette(self, app):
        pal = QPalette()

        pal.setColor(QPalette.Window, QColor("#f2f2f2"))
        pal.setColor(QPalette.WindowText, QColor("#202020"))

        pal.setColor(QPalette.Base, QColor("#ffffff"))
        pal.setColor(QPalette.AlternateBase, QColor("#f2f2f2"))
        pal.setColor(QPalette.Text, QColor("#202020"))

        pal.setColor(QPalette.Button, QColor("#e0e0e0"))
        pal.setColor(QPalette.ButtonText, QColor("#202020"))

        pal.setColor(QPalette.Mid, QColor("#c0c0c0"))
        pal.setColor(QPalette.Dark, QColor("#a0a0a0"))
        pal.setColor(QPalette.Light, QColor("#ffffff"))

        pal.setColor(QPalette.Highlight, QColor("#2979ff"))
        pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))

        app.setPalette(pal)

