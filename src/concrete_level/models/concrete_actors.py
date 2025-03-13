from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type
import numpy as np
from logical_level.models.actor_variable import ActorVariable, OSVariable, StaticObstacleVariable, TSVariable, VesselVariable
from logical_level.models.static_obstacle_types import StaticObstacleType
from logical_level.models.vessel_types import VesselType
from utils.serializable import Serializable

@dataclass(frozen=True)
class ConcreteActor(Serializable, ABC):
    id: int
    radius: float
    type : str
    
    @classmethod
    @abstractmethod
    def from_dict(cls: Type['ConcreteActor'], data: Dict[str, Any]) -> 'ConcreteActor':
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod    
    def logical_variable(self) -> ActorVariable:
        pass
    
    @property
    @abstractmethod
    def is_vessel(self) -> bool:
        pass
        
    def __repr__(self):
        return self.name

@dataclass(frozen=True)
class ConcreteStaticObstacle(ConcreteActor):
    
    @property
    def name(self) -> str:
        return f'SO_{self.id}'    

    
    @property
    def p(self) -> np.ndarray:
        return np.array([self.x, self.y])
    
    
    @property
    def logical_variable(self) -> 'StaticObstacleVariable':
        t = StaticObstacleType.get_static_obstacle_type_by_name(self.type)
        return StaticObstacleVariable(self.id, t)
        
    @classmethod
    def from_dict(cls: Type['ConcreteStaticObstacle'], data: Dict[str, Any]) -> 'ConcreteStaticObstacle':
        return ConcreteStaticObstacle(**data)
    
    @property
    def is_vessel(self) -> bool:
        return False
    
    
@dataclass(frozen=True)
class ConcreteVessel(ConcreteActor):
    is_os : bool
    length: float
    max_speed: float
    beam: Optional[float] = None
    
    @property
    def is_vessel(self) -> bool:
        return True
    
    @property
    def name(self) -> str:
        return f'OS_{self.id}' if self.is_os else f'TS_{self.id}'
    
    @property
    def max_turning_angle(self) -> float:
        return self.max_speed / 2.5 * self.length
    
    @property
    def max_acceleration(self) -> float:
        return self.max_speed**2 / (2* 15 * self.length)
    
    @property
    def logical_variable(self) -> VesselVariable:
        t = VesselType.get_vessel_type_by_name(self.type)
        return OSVariable(self.id, t) if self.is_os else TSVariable(self.id, t)
        
    @classmethod
    def from_dict(cls: Type['ConcreteVessel'], data: Dict[str, Any]) -> 'ConcreteVessel':
        return ConcreteVessel(**data)