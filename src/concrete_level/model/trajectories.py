from dataclasses import dataclass, asdict
import json
from typing import Dict, List
from concrete_level.model.concrete_vessel import ConcreteVessel
from concrete_level.model.vessel_state import VesselState
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from concrete_level.model.concrete_scene import ConcreteScene

@dataclass(frozen=True)
class Trajectories(Dict[ConcreteVessel, List[VesselState]]):   

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
    
    def get_initial_scene(self) -> ConcreteScene:
        return self.get_scene(0)
    