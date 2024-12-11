from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Set, Tuple

from functional_level.metamodels.vessel_class import FuncObject

@dataclass(frozen=True)
class Interpretation(ABC):
    name : str = ''
    _data : Set[tuple]
    
    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"
    
    @abstractmethod
    def contains(self, objects) -> bool:
        pass

    @abstractmethod
    def add(self, objects):
        pass
        
@dataclass()
class UnaryInterpretation(Interpretation, ABC):
    _data : Set[Tuple[FuncObject]]
    
    def contains(self, object : FuncObject) -> bool:
        return (object,) in self._data
    
    def add(self, object : FuncObject):
        self._data.add((object,))       
   
    
@dataclass()
class BinaryInterpretation(Interpretation, ABC):
    _data : Set[Tuple[FuncObject, FuncObject]]
    
    def contains(self, objects : Tuple[FuncObject, FuncObject]) -> bool:
        return objects in self._data
    
    def add(self, objects : Tuple[FuncObject, FuncObject]):
        self._data.add(objects)
        
    def get_tuples(self, o1 : Optional[FuncObject] = None, o2 : Optional[FuncObject] = None):
        tuples : Set[Tuple[FuncObject, FuncObject]] = set()
        for _o1, _o2 in self._data:
            if (o1 == _o1 or None) and (o2 == _o2 or None):
                tuples.add((_o1, _o2))
        return tuples
    
    def get_relation_descs(self, o : FuncObject) -> Set[Tuple[str, int, FuncObject]]:
        descs : Set[Tuple[str, int, FuncObject]] = set()
        for _o1, _o2 in self._data:
            if _o1 == o:
                descs.add((self.name, 1, _o2))
            elif _o2 == o:
                descs.add((self.name, 2, _o1))
        return descs
    
@dataclass()
class VesselInterpretation(UnaryInterpretation, ABC):
    pass

@dataclass()
class OSInterpretation(VesselInterpretation):
    name : str = 'OS'

@dataclass()
class TSInterpretation(VesselInterpretation):
    name : str = 'TS'

@dataclass()
class HeadOnInterpretation(BinaryInterpretation):
    name : str = 'HeadOn'

@dataclass()
class CrossingFromPortInterpretation(BinaryInterpretation):
    name : str = 'Crossing'

@dataclass()
class OvertakingInterpretation(BinaryInterpretation):
    name : str = 'Overtaking'


