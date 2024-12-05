from dataclasses import dataclass, field
from asv_utils import EPSILON, KNOT_TO_MS_CONVERSION
from functional_level.metamodels.vessel_class import VesselClass


THIRTY_KNOT_IN_MS = 30 * KNOT_TO_MS_CONVERSION
TWO_KNOT_IN_MS = 2 * KNOT_TO_MS_CONVERSION
@dataclass(frozen=True)
class VesselVariable():
    
    functional_class : VesselClass
    
    @property
    def max_speed(self) -> float:
        return THIRTY_KNOT_IN_MS
    
    @property
    def min_speed(self) -> float:
        return THIRTY_KNOT_IN_MS
    
    @property
    def max_length(self) -> float:
        return 30 + EPSILON if self.is_os else 100
    
    @property
    def min_length(self) -> float:
        return 30 - EPSILON if self.is_os else 10
    
    @property
    def id(self) -> int:
        return self.functional_class.id
    
    @property
    def is_os(self) -> bool:
        return self.functional_class.is_os()
    
    @property
    def name(self) -> str:
        return 'OS' if self.is_os else f'TS_{self.id}'
    
                
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    

 