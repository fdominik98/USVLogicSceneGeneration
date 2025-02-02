
from typing import Dict, Optional, Set, Tuple, Union

from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.vessel_state import VesselState
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from functional_level.metamodels.functional_scenario import FuncObject, FunctionalScenario
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache, GeometricProperties
from logical_level.models.actor_variable import ActorVariable
from logical_level.models.logical_scenario import LogicalScenario
from logical_level.models.relation_constraints import DoCollide, MayCollide


class MultiLevelScenario():
    def __init__(self, concrete_scene : ConcreteScene,
                 logical_scenario : LogicalScenario,  functional_scenario : FunctionalScenario):
        self.concrete_scene = concrete_scene
        self.logical_scenario = logical_scenario
        self.functional_scenario = functional_scenario
        
        self.concrete_actor_map : Dict[int, ConcreteVessel] = {actor.id : actor for actor in self.concrete_scene.actors}
        self.logical_actor_map : Dict[int, ActorVariable] = {actor.id : actor for actor in self.logical_scenario.actor_vars}
        self.functional_object_map : Dict[int, FuncObject] = {obj.id : obj for obj in self.functional_scenario.func_objects}
        self.evaluation_cache = EvaluationCache(self.concrete_scene.assignments(self.logical_scenario.actor_vars))
        
    def to_concrete_vessel(self, actor_or_obj : Union[ActorVariable, FuncObject]) -> ConcreteScene:
        return self.concrete_actor_map[actor_or_obj.id]
    
    def to_variable(self, actor_or_obj : Union[ConcreteVessel, FuncObject]) -> ActorVariable:
        return self.logical_actor_map[actor_or_obj.id]
    
    def to_object(self, actor_or_var : Union[ActorVariable, ConcreteVessel]) -> FuncObject:
        return self.functional_object_map[actor_or_var.id]
    
    def get_geo_props(self, actor1 : ConcreteVessel, actor2 : ConcreteVessel) -> GeometricProperties:
        var1, var2 = self.to_variable(actor1), self.to_variable(actor2)
        return self.evaluation_cache.get_props(var1, var2)
    
    def may_collide(self, actor1 : ConcreteVessel, actor2 : ConcreteVessel) -> bool:
        var1, var2 = self.to_variable(actor1), self.to_variable(actor2)
        may_collide = MayCollide(var1, var2)
        return may_collide._evaluate_penalty(self.evaluation_cache).is_zero
    
    def do_collide(self, actor1 : ConcreteVessel, actor2 : ConcreteVessel) -> bool:
        var1, var2 = self.to_variable(actor1), self.to_variable(actor2)
        do_collide = DoCollide(var1, var2)
        return do_collide._evaluate_penalty(self.evaluation_cache).is_zero
    
    def may_collide_anyone(self, actor1 : ConcreteVessel) -> bool:
        for actor2 in self.concrete_actor_map.values():
            if actor1 == actor2:
                continue
            if self.may_collide(actor1, actor2):
                return True
        return False
    
    @property
    def os_non_os_pairs(self) -> Set[Tuple[ConcreteVessel, ConcreteVessel]]:
        os = self.concrete_scene.os
        return {(os, actor) for actor in self.concrete_scene.non_os}
    
    def get_vessel_name(self, vessel : ConcreteVessel) -> str:
        return self.to_variable(vessel).name
    
    def modify_copy(self, vessel: ConcreteVessel, x : Optional[float] = None, y : Optional[float] = None,
        speed : Optional[float] = None, heading : Optional[float] = None) -> 'MultiLevelScenario':
        new_state = self.concrete_scene[vessel].modify_copy(x=x, y=y, speed=speed, heading=heading)
        new_scene = SceneBuilder(self.concrete_scene.as_dict()).set_state(vessel, new_state).build()
        return MultiLevelScenario(new_scene, self.logical_scenario, self.functional_scenario)