from abc import ABC, abstractmethod

class Scenario(ABC):
    @property
    @abstractmethod
    def size(self) -> int:
        pass