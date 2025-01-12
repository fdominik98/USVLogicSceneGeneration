from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from logical_level.models.actor_variable import OSVariable, TSVariable, VesselVariable
from utils.serializable import Serializable

@dataclass(frozen=True)
class ConcreteVessel(Serializable):
    id: int
    is_os : bool
    length: float
    radius: float
    max_speed: float
    breadth: Optional[float] = None
    
    def __repr__(self):
        return f'ConcreteVessel({self.id})'
    
    @property
    def max_turning_angle(self) -> float:
        return self.max_speed / 2.5 * self.length
    
    @property
    def max_acceleration(self) -> float:
        return self.max_speed**2 / (2* 15 * self.length)
    
    @property
    def logical_variable(self) -> VesselVariable:
        if self.is_os:
            return OSVariable(self.id)
        else:
            return TSVariable(self.id)
        
    @classmethod
    def from_dict(cls: Type['ConcreteVessel'], data: Dict[str, Any]) -> 'ConcreteVessel':
        return ConcreteVessel(**data)