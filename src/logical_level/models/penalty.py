from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Penalty():
    visibility_penalties : List[float]
    bearing_penalties : List[float]
    collision_penalties : List[float]
    
    @property
    def total_penalty(self) -> float:
        return sum(penalty for penalty in self.visibility_penalties +
                                 self.bearing_penalties +
                                 self.collision_penalties)
    @property    
    def total_visibility_penalty(self) -> float:
        return sum(self.visibility_penalties)
    
    @property    
    def total_collision_penalties_penalties_penalty(self) -> float:
        return sum(self.collision_penalties)
    
    @property    
    def total_visibility_penalty(self) -> float:
        return sum(self.visibility_penalties)
        
        
    def __add__(self, other):
        if isinstance(other, Penalty):
            return Penalty(self.visibility_penalties + other.visibility_penalties,
                           self.bearing_penalties + other.bearing_penalties,
                           self.collision_penalties + other.collision_penalties)
        return NotImplemented
    
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
        return f"{self.visibility_penalties}, {self.bearing_penalties}, {self.collision_penalties}"