from dataclasses import dataclass, asdict, field
import json
from typing import Optional

@dataclass(frozen=True)
class ConcreteVessel:
    id: int
    is_os : bool
    length: float
    radius: float
    max_speed: float
    breadth: Optional[float] = None
    max_turning_angle: float = field(init=False)
    max_acceleration: float = field(init=False)
    
    # Based on STANDARDS FOR SHIP MANOEUVRABILITY
    def __post_init__(self):
        object.__setattr__(self, 'max_turning_angle', self.max_speed / 2.5 * self.length)
        object.__setattr__(self, 'max_acceleration', self.max_speed**2 / (2* 15 * self.length))

    def to_json(self) -> str:
        """Serialize the class instance to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_string: str):
        """Deserialize a JSON string back into an instance of the class."""
        data = json.loads(json_string)
        return cls(**data)