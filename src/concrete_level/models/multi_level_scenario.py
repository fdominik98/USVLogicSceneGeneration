
from dataclasses import dataclass, field
from typing import Dict, Union

from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.trajectories import Trajectories
from functional_level.metamodels.functional_scenario import FuncObject, FunctionalScenario
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache
from logical_level.mapping.instance_initializer import RandomInstanceInitializer
from logical_level.models.actor_variable import ActorVariable
from logical_level.models.logical_scenario import LogicalScenario


dataclass(frozen=True)
class MultiLevelScenario():
    concrete_scene : ConcreteScene
    logical_scenario : LogicalScenario
    functional_scenario : FunctionalScenario
    
    concrete_actor_map : Dict[int, ConcreteVessel] = field(default_factory=dict, init=False)
    logical_actor_map : Dict[int, ActorVariable] = field(default_factory=dict, init=False)
    functional_object_map : Dict[int, FuncObject] = field(default_factory=dict, init=False)
    
    evaluation_cache : EvaluationCache = field(default=None, init=False)
    
    def __post_init__(self):
        object.__setattr__(self, 'concrete_actor_map', {actor.id for actor in self.concrete_scene.actors})
        object.__setattr__(self, 'logical_actor_map', {actor.id for actor in self.logical_scenario.actor_vars})
        object.__setattr__(self, 'functional_object_map', {obj.id for obj in self.functional_scenario.func_objects})
        object.__setattr__(self, 'evaluation_cache', {Assignments(self.logical_scenario.actor_vars).update_from_individual(self.concrete_scene.individual)})
        
    def to_concrete_vessel(self, actor_or_obj : Union[ActorVariable, FuncObject]) -> ConcreteScene:
        return self.concrete_actor_map[actor_or_obj.id]
    
    def to_variable(self, actor_or_obj : Union[ConcreteVessel, FuncObject]) -> ActorVariable:
        return self.logical_actor_map[actor_or_obj.id]
    
    def to_object(self, actor_or_var : Union[ActorVariable, ConcreteVessel]) -> FuncObject:
        return self.functional_object_map[actor_or_var.id]
    
    @staticmethod
    def from_concrete_scene(scene : ConcreteScene, init_method = RandomInstanceInitializer.name) -> 'MultiLevelScenario':
        logical_scenario, functional_scenario = ConcreteSceneAbstractor.get_abstractions_from_concrete(scene, init_method)
        return MultiLevelScenario(scene, logical_scenario, functional_scenario)