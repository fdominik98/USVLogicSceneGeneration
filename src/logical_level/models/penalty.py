from collections import defaultdict
from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional, Tuple

from logical_level.models.actor_variable import ActorVariable
from enum import Enum

class PenaltyCategory(Enum):
    VISIBILITY = "visibility_penalty"
    BEARING = "bearing_penalty"
    COLLISION = "collision_penalty"
    DIMENSION = "dimension_penalty"

    def __str__(self):
        return self.value

@dataclass(frozen=True)
class Penalty():
    actor_penalties : Dict[ActorVariable, float] = field(default_factory=lambda: defaultdict(float))

    visibility_penalty : float = 0
    bearing_penalty : float = 0
    collision_penalty : float = 0
    dimension_penalty : float = 0
    
    info : Dict[Tuple[ActorVariable, ActorVariable], List[str]] = field(default_factory=dict)
    
    category_num = 4
    
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
                
        merged_infos = {key: self.info.get(key, []) + other.info.get(key, []) for key in set(self.info) | set(other.info)}
                
        return Penalty(new_actor_penalties,
                        self.visibility_penalty + other.visibility_penalty,
                        self.bearing_penalty + other.bearing_penalty,
                        self.collision_penalty + other.collision_penalty,
                        self.dimension_penalty + other.dimension_penalty,
                        merged_infos)
    
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
        return self.total_penalty == 0.0
    
    def pretty_info(self, actors : Optional[Tuple[ActorVariable, ActorVariable]] = None) -> str:
        if actors is None:
            return '\n'.join([f"{key[0].name} → {key[1].name} : {json.dumps(value, indent=3)}" for key, value in self.info.items()])
        if actors not in self.info:
            return ''
        return json.dumps(self.info[actors], indent=3)