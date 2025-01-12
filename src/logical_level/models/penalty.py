from dataclasses import dataclass, field
from typing import Dict, Tuple

from logical_level.models.actor_variable import ActorVariable


@dataclass(frozen=True)
class Penalty():
    actor_penalties : Dict[ActorVariable, float] = field(default_factory=dict)
    
    visibility_penalty : float = 0
    bearing_penalty : float = 0
    collision_penalty : float = 0
    dimension_penalty : float = 0    
    
    category_num = 4
    
    info : str = ""
    
    @property
    def total_penalty(self) -> float:
        return self.visibility_penalty + self.bearing_penalty + self.collision_penalty + self.dimension_penalty
    
    @property
    def categorical_penalties(self) -> Tuple[float, float, float, float]:
        return (self.visibility_penalty, self.bearing_penalty, self.collision_penalty, self.dimension_penalty)
        
    def __add__(self, other):
        if not isinstance(other, Penalty):
            return NotImplemented
        
        new_actor_penalties = self.actor_penalties.copy()  # Start with a copy of dict1
        for var, value in other.actor_penalties.items():
            if var in new_actor_penalties:
                new_actor_penalties[var] += value  # Add values for keys present in both
            else:
                new_actor_penalties[var] = value   # Add new key-value pairs
                
        return Penalty(new_actor_penalties, self.visibility_penalty + other.visibility_penalty,
                        self.bearing_penalty + other.bearing_penalty,
                        self.collision_penalty + other.collision_penalty,
                        self.dimension_penalty + other.dimension_penalty,
                        f'{self.info}\n{other.info}')
    
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
        return f"penalty[{self.visibility_penalty}, {self.bearing_penalty}, {self.collision_penalty}, {self.dimension_penalty}]"
    
    @property
    def is_zero(self) -> bool:
        return self.total_penalty == 0