from dataclasses import dataclass, asdict
import json
from typing import Optional

@dataclass(frozen=True)
class ConcreteVessel:
    id: int
    length: float
    radius: float
    max_speed: float
    breadth: Optional[float] = None
    
    # Based on STANDARDS FOR SHIP MANOEUVRABILITY
    def __post_init__(self):
        self.max_turning_angle = self.max_speed / 2.5 * self.length # r/s
        self.max_acceleration = self.max_speed**2 / (2* 15 * self.length) # m/s^2

    def to_json(self) -> str:
        """Serialize the class instance to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_string: str):
        """Deserialize a JSON string back into an instance of the class."""
        data = json.loads(json_string)
        return cls(**data)