from typing import Dict
from concrete_level.model.concrete_vessel import ConcreteVessel
from concrete_level.model.vessel_state import VesselState
from src.concrete_level.model.concrete_scene import ConcreteScene


class SceneBuilder(Dict[ConcreteVessel, VesselState]):  
    def __init__(self, existing_dict=None, *args, **kwargs):
        # Initialize with an empty dict if no existing_dict is provided
        if existing_dict is None:
            existing_dict = {}
        # Call the parent constructor with the provided data
        super().__init__(existing_dict, *args, **kwargs)
    
    def set_state(self, vessel : ConcreteVessel, state : VesselState):
       self[vessel] = state
       
            
    def build(self):
        return ConcreteScene(self)