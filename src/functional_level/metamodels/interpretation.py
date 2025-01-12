from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Set, Tuple
from functional_level.metamodels.functional_scenario import FuncObject

@dataclass(frozen=True)
class Interpretation(ABC):
    name : str = ''
    _data : Set[tuple] = field(default_factory=set)
    
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
    def _add(self, objects):
        pass
        
@dataclass(frozen=True)
class UnaryInterpretation(Interpretation, ABC):
    _data : Set[Tuple[FuncObject]] = field(default_factory=set)
    
    def contains(self, object : FuncObject) -> bool:
        return (object,) in self._data
    
    def _add(self, objects : Tuple[FuncObject]):
        self._data.add(objects) 
        
    def add(self, object : FuncObject):
        self._add((object,))
        
    @property
    def next(self) -> FuncObject:
        return next(iter(self._data))[0]
    
@dataclass(frozen=True)
class BinaryInterpretation(Interpretation, ABC):
    _data : Set[Tuple[FuncObject, FuncObject]] = field(default_factory=set)
    
    def contains(self, objects : Tuple[FuncObject, FuncObject]) -> bool:
        return objects in self._data
    
    def _add(self, objects : Tuple[FuncObject, FuncObject]):
        self._data.add(objects)
        
    def add(self, o1 : FuncObject, o2 : FuncObject):
        self._add((o1, o2))
        
    def get_tuples(self, o1 : Optional[FuncObject] = None, o2 : Optional[FuncObject] = None):
        return {
            (t1, t2) for t1, t2 in self._data
            if (o1 is None or o1 == t1) and (o2 is None or o2 == t2)
        }
    
    def get_relation_descs(self, o : FuncObject) -> Set[Tuple[str, int, FuncObject]]:
        descs : Set[Tuple[str, int, FuncObject]] = set()
        for _o1, _o2 in self._data:
            if _o1 == o:
                descs.add((self.name, 1, _o2))
            elif _o2 == o:
                descs.add((self.name, 2, _o1))
        return descs
    
@dataclass(frozen=True)
class VesselInterpretation(UnaryInterpretation, ABC):
    pass

@dataclass(frozen=True)
class OSInterpretation(VesselInterpretation):
    name : str = field(default='OS', init=False)

@dataclass(frozen=True)
class TSInterpretation(VesselInterpretation):
    name : str = field(default='TS', init=False)

@dataclass(frozen=True)
class HeadOnInterpretation(BinaryInterpretation):
    name : str = field(default='HeadOn', init=False)

@dataclass(frozen=True)
class CrossingFromPortInterpretation(BinaryInterpretation):
    name : str = field(default='Crossing', init=False)

@dataclass(frozen=True)
class OvertakingInterpretation(BinaryInterpretation):
    name : str = field(default='Overtaking', init=False)



