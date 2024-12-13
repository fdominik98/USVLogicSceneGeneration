from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import numpy as np
from asv_utils import EPSILON, KNOT_TO_MS_CONVERSION, MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING


THIRTY_KNOT_IN_MS = 30 * KNOT_TO_MS_CONVERSION
TWO_KNOT_IN_MS = 2 * KNOT_TO_MS_CONVERSION
@dataclass(frozen=True)
class ActorVariable(ABC):    
    scope_id : int
    id : int
    
    @abstractmethod
    @property
    def name(self) -> str:
        pass
                
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    
    @abstractmethod
    @property
    def upper_bounds(self) -> List[float]:
        pass
    
    @abstractmethod
    @property
    def lower_bounds(self) -> List[float]:
        pass
    
    def __len__(self) -> int:
        return len(self.lower_bounds)
    

@dataclass(frozen=True)    
class VesselVariable(ActorVariable, ABC):    
    @property
    def max_speed(self) -> float:
        return THIRTY_KNOT_IN_MS
    
    @property
    def min_speed(self) -> float:
        return THIRTY_KNOT_IN_MS
    
    @property
    def max_length(self) -> float:
        return 100
    
    @property
    def min_length(self) -> float:
        return 10
    
    @property
    def max_heading(self) -> float:
        return MAX_HEADING
    
    @property
    def min_heading(self) -> float:
        return MIN_HEADING
    
    @property
    def max_coord(self) -> float:
        return MAX_COORD
    
    @property
    def min_coord(self) -> float:
        return MIN_COORD
    
    @abstractmethod
    @property
    def is_os(self) -> bool:
        pass
    
    @abstractmethod
    @property
    def name(self) -> str:
        pass
    
    @property
    def upper_bounds(self) -> List[float]:
        return [self.max_coord, self.max_coord, self.max_heading, self.max_length, self.max_speed]
    
    @property
    def lower_bounds(self) -> List[float]:
        return [self.min_coord, self.min_coord, self.min_heading, self.min_length, self.min_speed]
    
@dataclass(frozen=True)   
class OSVariable(VesselVariable):
    @property
    def max_length(self) -> float:
        return 30 + EPSILON
    
    @property
    def min_length(self) -> float:
        return 30 - EPSILON
    
    @property
    def max_heading(self) -> float:
        return np.pi / 2 + EPSILON
    
    @property
    def min_heading(self) -> float:
        return np.pi / 2 - EPSILON
    
    @property
    def max_coord(self) -> float:
        return MAX_COORD / 2 + EPSILON
    
    @property
    def min_coord(self) -> float:
        return MAX_COORD / 2 - EPSILON
    
    @property
    def name(self) -> str:
        return f'OS_{self.id}'
    
    @property
    def is_os(self) -> bool:
        return True

@dataclass(frozen=True)    
class TSVariable(VesselVariable):    
    @property
    def name(self) -> str:
        return f'TS_{self.id}'
    
    @property
    def is_os(self) -> bool:
        return False
    
 