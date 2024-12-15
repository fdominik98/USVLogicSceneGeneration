from dataclasses import dataclass
from typing import List
import numpy as np
from logical_level.mapping.instance_initializer import InstanceInitializer
from logical_level.models.relation_constraints import RelationConstrClause
from logical_level.models.actor_variable import ActorVariable

@dataclass(frozen=True)
class LogicalScenario():
    initializer : InstanceInitializer
    relation_constr_clause : RelationConstrClause
    xl : List[float]
    xu : List[float]   
    
    @property
    def actor_vars(self) -> List[ActorVariable]:
        return self.initializer.actor_vars
    
    @property
    def actor_num(self) -> int:
        return len(self.actor_vars)
    
    @property
    def all_variable_num(self) -> int:
        return len(self.xl)
    
    def get_population(self, pop_size) -> List[List[float]]:
        population = self.initializer.get_population(pop_size=pop_size)
        return population
    
    def pop_to_np_array(self, pop : List[List[float]]):
        new_pop = []
        for p in pop :
            new_pop.append(np.array(p))
        return np.array(new_pop)
    
    def get_vessel_by_id(self, id):
        vessel_var = next((v for v in self.actor_vars if v.id == id), None)
        if vessel_var is None:
            raise Exception(f"No vessel with id {id}")
        return vessel_var    
    