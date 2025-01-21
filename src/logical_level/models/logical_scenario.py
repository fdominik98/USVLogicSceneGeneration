from dataclasses import dataclass
from typing import List
import numpy as np
from logical_level.mapping.instance_initializer import InstanceInitializer
from logical_level.models.relation_constraints import RelationConstrComposite
from logical_level.models.actor_variable import ActorVariable
from utils.scenario import Scenario

@dataclass(frozen=True)
class LogicalScenario(Scenario):
    initializer : InstanceInitializer
    relation_constraint : RelationConstrComposite
    xl : List[float]
    xu : List[float]   
    
    @property
    def actor_vars(self) -> List[ActorVariable]:
        return self.initializer.actor_vars
    
    @property
    def size(self) -> int:
        return len(self.actor_vars)
    
    @property
    def all_variable_num(self) -> int:
        return len(self.xl)
    
    @property
    def name(self) -> str:
        return f'{str(self.size)}vessel'
    
    def get_population(self, pop_size) -> List[List[float]]:
        population = self.initializer.get_population(pop_size=pop_size)
        return population
    
    def pop_to_np_array(self, pop : List[List[float]]):
        new_pop = []
        for p in pop :
            new_pop.append(np.array(p))
        return np.array(new_pop)
    
 