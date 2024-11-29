import math
from typing import List

import numpy as np
from model.instance_initializer import RandomInstanceInitializer, DeterministicInitializer, LatinHypercubeInitializer
from model.environment.usv_environment_desc import USVEnvironmentDesc, MSREnvironmentDesc
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING, OWN_VESSEL_STATES, VARIABLE_NUM
from evolutionary_computation.evaluation_data import EvaluationData
from evaluation.eqv_class_calculator import EqvClassCalculator

class USVEnvironment():
    def __init__(self, env_config : USVEnvironmentDesc, init_method='uniform') -> None:
        self.config = env_config
        if init_method == 'uniform': 
            self.initializer = RandomInstanceInitializer(self.config.vessel_descs, self.config.relation_desc_clauses) 
        elif init_method == 'deterministic':
            self.initializer = DeterministicInitializer(self.config.vessel_descs, self.config.relation_desc_clauses) 
        elif init_method == 'lhs':
            self.initializer = LatinHypercubeInitializer(self.config.vessel_descs, self.config.relation_desc_clauses) 
        else:
            raise Exception('unknown parameter')
            
        self.vessels, self.relation_clauses = self.initializer.get_one_population_as_objects()    
        self.clause = min(self.relation_clauses, key=lambda clause: clause.penalties_sum)
        self.relations = self.clause.relations
          
        self.xl, self.xu = self.generate_gene_space()
        
    def update(self, states : List[float]):
        if len(states) != self.config.all_variable_num:
            raise Exception("the variable number is insufficient.")
        
        states = OWN_VESSEL_STATES + states
        return self.do_update(states)
    
    def do_update(self, states : List[float]):
        if len(states) != VARIABLE_NUM * self.config.vessel_num:
            raise Exception("the variable number is insufficient.")
        
        for vessel in self.vessels:
            vessel.update(states[vessel.id * VARIABLE_NUM],
                                states[vessel.id * VARIABLE_NUM + 1],
                                states[vessel.id * VARIABLE_NUM + 2],
                                states[vessel.id * VARIABLE_NUM + 3],
                                states[vessel.id * VARIABLE_NUM + 4])
        
        for clause in self.relation_clauses:
            clause.update()
        self.clause = min(self.relation_clauses, key=lambda clause: clause.penalties_sum)
        self.relations = self.clause.relations  
        
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
        vessel = next((v for v in self.vessels if v.id == id), None)
        if vessel is None:
            raise Exception(f"No vessel with id {id}")
        return vessel
    
    # Attribute generator with different boundaries
    def generate_gene_space(self):
        xl = [self.config.vessel_descs[0].min_length, self.config.vessel_descs[0].min_speed]
        xu = [self.config.vessel_descs[0].max_length, self.config.vessel_descs[0].max_speed]
        for vessel_desc in self.config.vessel_descs[1:]:
            xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel_desc.min_length, vessel_desc.min_speed]
            xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel_desc.max_length, vessel_desc.max_speed]
        return xl, xu
    
    
class LoadedEnvironment(USVEnvironment):
    def __init__(self, eval_data : EvaluationData, init_method='uniform'):
        vessel_descs, clause = EqvClassCalculator().get_clause(eval_data)
        config = MSREnvironmentDesc(0, vessel_descs, [clause])
        super().__init__(config, init_method)
        self.update(eval_data.best_solution)
