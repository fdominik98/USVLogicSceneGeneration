from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from logical_level.models.vessel_types import PassengerShip, VesselType
from utils.asv_utils import EPSILON, MAX_BEAM, MAX_COORD, MAX_HEADING, MAX_LENGTH, MAX_SPEED_IN_MS, MIN_BEAM, MIN_COORD, MIN_HEADING, MIN_LENGTH, MIN_SPEED_IN_MS

@dataclass(frozen=True)
class ActorVariable(ABC):    
    id : int
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
                
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    
    @property
    @abstractmethod
    def upper_bounds(self) -> List[float]:
        pass
    
    @property
    @abstractmethod
    def lower_bounds(self) -> List[float]:
        pass
    
    def __len__(self) -> int:
        return len(self.lower_bounds)
    

@dataclass(frozen=True)    
class VesselVariable(ActorVariable, ABC):
    
    vessel_type : Optional[VesselType] = None
    
    @property
    def min_length(self) -> float:
        if self.vessel_type is None:
            return MIN_LENGTH
        return self.vessel_type.min_length
    
    @property
    def max_length(self) -> float:
        if self.vessel_type is None:
            return MAX_LENGTH
        return self.vessel_type.max_length
    
    @property
    def min_beam(self) -> float:
        if self.vessel_type is None:
            return MIN_BEAM
        return self.vessel_type.min_beam
    
    @property
    def max_beam(self) -> float:
        if self.vessel_type is None:
            return MAX_BEAM
        return self.vessel_type.max_beam
        
    @property
    def min_speed(self) -> float:
        if self.vessel_type is None:
            return MIN_SPEED_IN_MS
        return self.vessel_type.min_speed
    
    @property
    def max_speed(self) -> float:
        if self.vessel_type is None:
            return MAX_SPEED_IN_MS
        return self.vessel_type.max_speed
    
    @property
    def min_heading(self) -> float:
        return MIN_HEADING
    
    @property
    def max_heading(self) -> float:
        return MAX_HEADING
    
    @property
    def min_coord(self) -> float:
        return MIN_COORD
    
    @property
    def max_coord(self) -> float:
        return MAX_COORD
    
    @property
    @abstractmethod
    def is_os(self) -> bool:
        pass
    
    @property
    @abstractmethod
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
    vessel_type : Optional[VesselType] = PassengerShip()
    
    @property
    def min_length(self) -> float:
        return 30 - EPSILON
    
    @property
    def max_length(self) -> float:
        return 30 + EPSILON
    
    @property
    def min_beam(self) -> float:
        return 10 - EPSILON
    
    @property
    def max_beam(self) -> float:
        return 10 + EPSILON
    
    @property
    def min_heading(self) -> float:
        return np.pi / 2 - EPSILON
    
    @property
    def max_heading(self) -> float:
        return np.pi / 2 + EPSILON
    
    @property
    def min_coord(self) -> float:
        return MAX_COORD / 2 - EPSILON
    
    @property
    def max_coord(self) -> float:
        return MAX_COORD / 2 + EPSILON
    
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
    
 