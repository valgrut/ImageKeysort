from enum import Enum


class Operations(Enum):
    MOVE = 1
    COPY = 2

    def __str__(self):
        return self.name