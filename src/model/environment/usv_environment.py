from dataclasses import dataclass
from typing import List, Set
import numpy as np
from logical_level.mapping.instance_initializer import InstanceInitializer, RandomInstanceInitializer, DeterministicInitializer, LatinHypercubeInitializer
from model.environment.usv_environment_desc import USVEnvironmentDesc, MSREnvironmentDesc
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING, OWN_VESSEL_STATES
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from evaluation.eqv_class_calculator import EqvClassCalculator
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.model.vessel_variable import VesselVariable
from model.relation import Relation, RelationClause

@dataclass(frozen=True)
class LogicalScenario():
    config : USVEnvironmentDesc
    initializer : InstanceInitializer
    assignments : Assignments
    xl : List[float]
    xu : List[float]   
    
    @property
    def vessel_vars(self) -> List[VesselVariable]:
        return list(self.assignments.keys())
    
    @property
    def clauses(self) -> Set[RelationClause]:
        return self.assignments.registered_clauses
    
    @property
    def relations(self) -> List[Relation]:
        return self.assignments.relations
        
    def update(self, states : List[float]):
        if len(states) != self.config.all_variable_num:
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
    