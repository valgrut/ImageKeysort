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
    def getDefaultButtonStyles() -> str:
        return f"""
            QPushButton {{
                __width: 150px;
                height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                padding: 3px;
                background-color: {Styles.buttonBgColor};
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {Styles.buttonHoverBgColor};
            }}
        """

    @staticmethod
    def getActiveButtonStyles() -> str:
        return f"""
            QPushButton {{
                __width: 150px;
                height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                padding: 3px;
                background-color: {Styles.buttonActivatedBgColor};
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {Styles.buttonHoverBgColor};
            }}
        """
    
    @staticmethod
    def getShadowEffect():
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setOffset(3, 3)
        shadowEffect.setBlurRadius(10)
        return shadowEffect
