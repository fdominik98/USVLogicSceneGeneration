from dataclasses import dataclass, field
from asv_utils import EPSILON, KNOT_TO_MS_CONVERSION
from functional_level.metamodels.vessel_class import VesselClass

@dataclass(frozen=True)
class VesselVariable():
    
    desc : VesselClass
    
    max_speed: float = field(init=False)
    min_speed: float = field(init=False)
    max_length: float = field(init=False)
    min_length: float = field(init=False)
    id: float = field(init=False)
    is_os: bool = field(init=False)
    name: str = field(init=False)
    
    def __post_init__(self):
        object.__setattr__(self, 'max_speed', 30 * KNOT_TO_MS_CONVERSION) # kn
        object.__setattr__(self, 'min_speed', 2 * KNOT_TO_MS_CONVERSION)
        object.__setattr__(self, 'max_length', 100) # m
        object.__setattr__(self, 'min_length', 10)
        object.__setattr__(self, 'id', self.desc.id)
        object.__setattr__(self, 'is_os', self.desc.is_os())
        if self.is_os:
            object.__setattr__(self, 'max_length', 30 + EPSILON) # m
            object.__setattr__(self, 'min_length', 30 - EPSILON)
            object.__setattr__(self, 'name', 'OS')
        else:
            object.__setattr__(self, 'name', f'TS_{self.id}')
                
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    

 