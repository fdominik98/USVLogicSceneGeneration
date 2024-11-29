from dataclasses import dataclass, asdict
import json

import numpy as np

@dataclass(frozen=True)
class VesselState:
    x : float
    y : float
    speed : float
    heading : float
    
    # Based on 
    def __post_init__(self):
        self.p = np.array([self.x, self.y])
        self.v = np.array([np.cos(self.heading), np.sin(self.heading)]) * self.speed
        self.v_norm = self.v / self.speed
        self.v_norm_perp = np.array([self.v_norm[1], -self.v_norm[0]])
        
    def to_json(self) -> str:
        """Serialize the class instance to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_string: str):
        """Deserialize a JSON string back into an instance of the class."""
        data = json.loads(json_string)
        return cls(**data)