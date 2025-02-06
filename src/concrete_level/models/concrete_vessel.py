from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from logical_level.models.actor_variable import OSVariable, TSVariable, VesselVariable
from logical_level.models.vessel_types import VesselType
from utils.serializable import Serializable

@dataclass(frozen=True)
class ConcreteVessel(Serializable):
    id: int
    is_os : bool
    length: float
    radius: float
    max_speed: float
    vessel_type : str
    beam: Optional[float] = None
    
    @property
    def name(self) -> str:
        return f'OS_{self.id}' if self.is_os else f'TS_{self.id}'
    
    def __repr__(self):
        return self.name
    
    @property
    def max_turning_angle(self) -> float:
        return self.max_speed / 2.5 * self.length
    
    @property
    def max_acceleration(self) -> float:
        return self.max_speed**2 / (2* 15 * self.length)
    
    @property
    def logical_variable(self) -> VesselVariable:
        t = VesselType.get_vessel_type_by_name(self.vessel_type)
        if t is None :
            raise TypeError('Vessel type is not found')
        if self.is_os:
            return OSVariable(self.id, t)
        else:
            return TSVariable(self.id, t)
        
    @classmethod
    def from_dict(cls: Type['ConcreteVessel'], data: Dict[str, Any]) -> 'ConcreteVessel':
        return ConcreteVessel(**data)