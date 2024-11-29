from dataclasses import asdict, dataclass
import json
from typing import Dict

from src.concrete_level.model.concrete_vessel import ConcreteVessel
from src.concrete_level.model.vessel_state import VesselState


@dataclass(frozen=True)
class ConcreteScene(Dict[ConcreteVessel, VesselState]):   

    def to_json(self) -> str:
        """Serialize the class instance to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_string: str):
        """Deserialize a JSON string back into an instance of the class."""
        data = json.loads(json_string)
        return cls(**data)