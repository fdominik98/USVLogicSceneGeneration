from dataclasses import dataclass, asdict
import json
from typing import Dict, List
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.vessel_state import VesselState
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from concrete_level.models.concrete_scene import ConcreteScene

@dataclass(frozen=True)
class Trajectories:  
    _data : Dict[ConcreteVessel, List[VesselState]]
    
    def __post_init__(self):
        object.__setattr__(self, '_data', dict(self._data))
            
    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})" 

    def to_json(self) -> str:
        """Serialize the class instance to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_string: str):
        """Deserialize a JSON string back into an instance of the class."""
        data = json.loads(json_string)
        return cls(**data)
    
    def get_scene(self, t : int) -> ConcreteScene:
        sb = SceneBuilder()
        for vessel, states in self.items():
            sb.set_state(vessel, states[t])
        return sb.build()
   
    @property 
    def initial_scene(self) -> ConcreteScene:
        return self.get_scene(0)
    