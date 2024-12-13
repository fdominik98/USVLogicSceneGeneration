from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from logical_level.models.vessel_variable import ActorVariable


@dataclass(frozen=True)
class Penalty():
    visibility_penalties : List[float]
    bearing_penalties : List[float]
    collision_penalties : List[float]
    actor_penalties : Dict[ActorVariable, float]
    
    @property
    def total_penalty(self) -> float:
        return sum(penalty for penalty in self.visibility_penalties +
                                 self.bearing_penalties +
                                 self.collision_penalties)
    @property    
    def total_visibility_penalty(self) -> float:
        return sum(self.visibility_penalties)
    
    @property    
    def total_collision_penalties(self) -> float:
        return sum(self.collision_penalties)
    
    @property    
    def total_bearing_penalties(self) -> float:
        return sum(self.bearing_penalties)
    
    @property    
    def total_categorical_penalties(self) -> Tuple[float, float, float]:
        return (self.total_visibility_penalty, self.total_bearing_penalties, self.total_collision_penalties)
        
        
    def __add__(self, other):
        if not isinstance(other, Penalty):
            return NotImplemented
        
        new_actor_penalties = self.actor_penalties.copy()  # Start with a copy of dict1
        for var, value in other.actor_penalties.items():
            if var in new_actor_penalties:
                new_actor_penalties[var] += value  # Add values for keys present in both
            else:
                new_actor_penalties[var] = value   # Add new key-value pairs
                
        return Penalty(self.visibility_penalties + other.visibility_penalties,
                        self.bearing_penalties + other.bearing_penalties,
                        self.collision_penalties + other.collision_penalties,
                        new_actor_penalties)
    
    def __eq__(self, other):
        if isinstance(other, Penalty):
            return self.total_penalty == other.total_penalty
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Penalty):
            return self.total_penalty < other.total_penalty
        return NotImplemented

    def __le__(self, other):
        return self == other or self < other

    def __repr__(self):
        return f"penalty[{self.visibility_penalties}, {self.bearing_penalties}, {self.collision_penalties}]"