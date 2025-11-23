from abc import ABC, abstractmethod

class ModeHandler(ABC):
    @abstractmethod
    def start_engine(self):
        pass