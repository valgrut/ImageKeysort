from enum import Enum


class Themes(Enum):
    LIGHT = 1
    DARK = 2
    NIGHT = 3
    RETRO = 4

    def __str__(self):
        return self.name
