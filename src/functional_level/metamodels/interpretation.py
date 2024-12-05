from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

from src.functional_level.metamodels.vessel_class import FuncObject

@dataclass(frozen=True)
class Interpretation(ABC):
    @abstractmethod
    def add(self, object):
        pass
    
    @abstractmethod
    def contains(self, object) -> bool:
        pass


@dataclass()
class UnaryInterpretation(Interpretation, ABC):
    _data : List[Tuple[FuncObject]]
    
    def contains(self, object : FuncObject) -> bool:
        return (object,) in self._data
    
@dataclass()
class BinaryInterpretation(Interpretation, ABC):
    _data : List[Tuple[FuncObject, FuncObject]]
    
    def contains(self, objects : Tuple[FuncObject, FuncObject]) -> bool:
        return objects in self._data
    
    
@dataclass()
class VesselInterpretation(UnaryInterpretation, ABC):
    pass

@dataclass()
class OSInterpretation(VesselInterpretation):
    pass

@dataclass()
class TSInterpretation(VesselInterpretation):
    pass

@dataclass()
class HeadOnInterpretation(BinaryInterpretation):
    pass

@dataclass()
class CrossingFromPortInterpretation(BinaryInterpretation):
    pass

@dataclass()
class OvertakingInterpretation(BinaryInterpretation):
    pass


