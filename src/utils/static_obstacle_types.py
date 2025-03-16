from abc import ABC
from dataclasses import dataclass
from typing import List, Optional

from utils.asv_utils import MIN_OBSTACLE_RADIUS, MAX_OBSTACLE_RADIUS


@dataclass(frozen=True, repr=False)
class StaticObstacleType(ABC):
    name : str = 'StaticObstacleType'
    min_radius : float = MIN_OBSTACLE_RADIUS
    max_radius : float = MAX_OBSTACLE_RADIUS
    
    def do_match(self, radius : float) -> bool:
        return (self.min_radius <= radius <= self.max_radius)
        
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
        
    @staticmethod    
    def get_static_obstacle_type_by_name(name : Optional[str]):
        if name is None:
            return DEFAULT_OBSTACLE_TYPE
        return next((t for t in ALL_STATIC_OBSTACLE_TYPES if t.name == name))
    
    @property
    def is_unspecified(self) -> bool:
        return False
    
@dataclass(frozen=True, repr=False)
class UnspecifiedObstacleType(StaticObstacleType):
    name : str = 'UnspecifiedType'
    
    @property
    def is_unspecified(self) -> bool:
        return True

@dataclass(frozen=True, repr=False)
class OtherObstacleType(StaticObstacleType):
    name : str = 'OtherType'
    pass   
    
@dataclass(frozen=True, repr=False)
class SmallObstacle(StaticObstacleType):
    name : str = 'SmallObstacle'
    max_radius : float = 50
    
@dataclass(frozen=True, repr=False)
class MediumObstacle(StaticObstacleType):
    name : str = 'MediumObstacle'
    min_radius : float = 50
    max_radius : float = 200
    
@dataclass(frozen=True, repr=False)
class LargeObstacle(StaticObstacleType):
    name : str = 'LargeObstacle'
    min_radius : float = 200
    
ALL_STATIC_OBSTACLE_TYPES : List[StaticObstacleType] = [OtherObstacleType(), SmallObstacle(), MediumObstacle(), LargeObstacle()]
DEFAULT_OBSTACLE_TYPE = UnspecifiedObstacleType()