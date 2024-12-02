from typing import Dict, List
from concrete_level.model.concrete_vessel import ConcreteVessel
from concrete_level.model.vessel_state import VesselState
from src.concrete_level.model.concrete_scene import ConcreteScene
from src.concrete_level.model.trajectories import Trajectories


class TrajectoryBuilder(Dict[ConcreteVessel, List[VesselState]]):  
    def __init__(self, existing_dict={}, *args, **kwargs):
        super().__init__(existing_dict, *args, **kwargs)
    
    def add_state(self, vessel : ConcreteVessel, state : VesselState):
        if vessel not in self:
            self[vessel] = [state]
        else:
            self[vessel].append(state)
            
    def add_scene(self, scene: ConcreteScene):
        for vessel, state in scene.items():
            self.add_state(vessel, state)
            
    def build(self):
        return Trajectories(self)