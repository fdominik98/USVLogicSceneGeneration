from dataclasses import dataclass
from typing import List, Set
import numpy as np
from logical_level.mapping.instance_initializer import InstanceInitializer
from functional_level.metamodels.functional_scenario import FunctionalScenario
from asv_utils import OWN_VESSEL_STATES, VARIABLE_NUM
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.vessel_variable import VesselVariable
from logical_level.models.relation_constraint import RelationConstr, RelationConstrTerm

@dataclass(frozen=True)
class LogicalScenario():
    config : FunctionalScenario
    initializer : InstanceInitializer
    assignments : Assignments
    xl : List[float]
    xu : List[float]   
    
    def __post_init__(self):
        if self.vessel_num != self.config.vessel_num:
            raise ValueError(f"Inconsistent vessel numbers: {self.vessel_num} != {self.config.vessel_num}")
    
    @property
    def vessel_vars(self) -> List[VesselVariable]:
        return list(self.assignments.keys())
    
    @property
    def vessel_num(self) -> int:
        return len(self.vessel_vars)
    
    @property
    def all_variable_num(self) -> int:
        return VARIABLE_NUM * self.vessel_num - (VARIABLE_NUM - 2)
    
    @property
    def clauses(self) -> Set[RelationConstrTerm]:
        return self.assignments.registered_clauses
    
    @property
    def relations(self) -> List[RelationConstr]:
        return self.assignments.relations
        
    def update(self, states : List[float]):
        if len(states) != self.all_variable_num:
            raise Exception("the variable number is insufficient.")        
        states = OWN_VESSEL_STATES + states
        return self.do_update(states)
    
    def do_update(self, states : List[float]):
        self.assignments.update_from_population(states)             
        return self
    
         
    def get_population(self, pop_size) -> List[List[float]]:
        population = self.initializer.get_population(pop_size=pop_size)
        return population
    
    def pop_to_np_array(self, pop : List[List[float]]):
        new_pop = []
        for p in pop :
            new_pop.append(np.array(p))
        return np.array(new_pop)
    
    def get_vessel_by_id(self, id):
        vessel_var = next((v for v in self.vessel_vars if v.id == id), None)
        if vessel_var is None:
            raise Exception(f"No vessel with id {id}")
        return vessel_var    
    