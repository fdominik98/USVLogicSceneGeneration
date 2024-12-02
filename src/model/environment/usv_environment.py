from typing import List
import numpy as np
from logical_level.mapping.instance_initializer import RandomInstanceInitializer, DeterministicInitializer, LatinHypercubeInitializer
from model.environment.usv_environment_desc import USVEnvironmentDesc, MSREnvironmentDesc
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING, OWN_VESSEL_STATES
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
        
        self.vessels = self.initializer.vessel_vars
        self.assignments = self.initializer.assignments
          
        self.xl, self.xu = self.generate_gene_space()
        
    def update(self, states : List[float]):
        if len(states) != self.config.all_variable_num:
            raise Exception("the variable number is insufficient.")
        
        states = OWN_VESSEL_STATES + states
        return self.do_update(states)
    
    def do_update(self, states : List[float]):
        self.assignments.update_from_population(states)
        
        self.clause = min(self.assignments.registered_clauses, key=lambda clause: clause.penalties_sum)
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
        xl = [self.vessels[0].min_length, self.vessels[0].min_speed]
        xu = [self.vessels[0].max_length, self.vessels[0].max_speed]
        for vessel in self.vessels[1:]:
            xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel.min_length, vessel.min_speed]
            xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel.max_length, vessel.max_speed]
        return xl, xu
    
    
class LoadedEnvironment(USVEnvironment):
    def __init__(self, eval_data : EvaluationData, init_method='uniform'):
        vessel_descs, clause = EqvClassCalculator().get_clause(eval_data)
        config = MSREnvironmentDesc(0, vessel_descs, [clause])
        super().__init__(config, init_method)
        self.update(eval_data.best_solution)
