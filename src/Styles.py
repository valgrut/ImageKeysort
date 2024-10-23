

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
    def getButtonStyles():
        return f"""
        QPushButton {{
            __width: 150px;
            border: 1px solid black;
            border-radius: {Styles.buttonBorderRadius}px;
            padding: 3px;
            background-color: rgb(191, 189, 189);
            font-weight: bold;
            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: yellow;
        }}
        """
