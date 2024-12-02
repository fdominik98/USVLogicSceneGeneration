from dataclasses import asdict, dataclass, field
import json
from typing import Dict, Optional
from concrete_level.model.concrete_vessel import ConcreteVessel
from concrete_level.model.vessel_state import VesselState


@dataclass(frozen=True)
class ConcreteScene(Dict[ConcreteVessel, VesselState]):   
    
    dcpa : Optional[float] = None
    tcpa : Optional[float] = None
    danger_sector : Optional[float] = None
    proximity_index : Optional[float] = None
    
    vessel_number : int = field(init=False)
    
    def __post_init__(self):
        object.__setattr__(self, 'vessel_number', len(self))
    
    def to_json(self) -> str:
        """Serialize the class instance to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_string: str):
        """Deserialize a JSON string back into an instance of the class."""
        data = json.loads(json_string)
        return cls(**data)    
    