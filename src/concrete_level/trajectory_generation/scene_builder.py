from typing import Dict
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.vessel_state import VesselState
from concrete_level.models.concrete_scene import ConcreteScene
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.actor_variable import VesselVariable


class SceneBuilder(Dict[ConcreteVessel, VesselState]):  
    def __init__(self, existing_dict=None, *args, **kwargs):
        # Initialize with an empty dict if no existing_dict is provided
        if existing_dict is None:
            existing_dict = {}
        # Call the parent constructor with the provided data
        super().__init__(existing_dict, *args, **kwargs)
    
    def set_state(self, vessel : ConcreteVessel, state : VesselState):
       self[vessel] = state
       
            
    def build(self) -> ConcreteScene:
        return ConcreteScene(self)
    
    @staticmethod
    def build_from_assignments(assignments : Assignments) -> ConcreteScene:
        builder = SceneBuilder()
        for actor_var, values in assignments.items():
            if isinstance(actor_var, VesselVariable):
                builder.set_state(ConcreteVessel(actor_var.is_os, actor_var.id, values.l, values.r, actor_var.max_speed),
                                  VesselState(values.x, values.y, values.sp, values.h))
        return builder.build()