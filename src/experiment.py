import re

class Widget():
    def __init__(self):
        self._stylesheets = f"""
            width: 100px;
            border: 1px solid black;
            border-radius: 10px;
            padding: 3px;
            background-color: rgb(100, 100, 189);
        """

    def stylesheet(self):
        return self._stylesheets

    def setStylesheet(self, style):
        self._stylesheets = style


def updateStylesheet(widget, updatedValues):
    # Separate new values
    listOfValues = updatedValues.split(';')

    # Clean the new values
    for i, updatedValue in enumerate(listOfValues):
        listOfValues[i] = updatedValue.strip()

    # TODO: skip for example QLabel, {, }, and such. Skip anything not matching pattern: '[a-z-]:'
    currentStyle = widget.stylesheet()
    for line in listOfValues:
        splittedValue = line.split(":")
        if len(splittedValue) == 1:
            break
        updatedValue = splittedValue[0] + ":" + splittedValue[1] + ";"
        print(updatedValue)
        currentStyle = re.sub(splittedValue[0]+":.*;", updatedValue, currentStyle)

    widget.setStylesheet(currentStyle)


w = Widget()
print(w.stylesheet())
updateStylesheet(w, f"""
        border: 3px solid orange;padding: 7px;
        width: 200px;
""")
print(w.stylesheet())