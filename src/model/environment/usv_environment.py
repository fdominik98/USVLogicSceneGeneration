import math
from typing import List

import numpy as np
from model.instance_initializer import RandomInstanceInitializer, DeterministicInitializer, LatinHypercubeInitializer
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING, OWN_VESSEL_STATES, VARIABLE_NUM


class USVEnvironment():
    def __init__(self, env_config : USVEnvironmentDesc, init_method='uniform') -> None:
        self.config = env_config
        if init_method == 'uniform': 
            self.initializer = RandomInstanceInitializer(self.config.vessel_descs, self.config.colreg_situation_descs) 
        elif init_method == 'deterministic':
            self.initializer = DeterministicInitializer(self.config.vessel_descs, self.config.colreg_situation_descs) 
        elif init_method == 'lhs':
            self.initializer = LatinHypercubeInitializer(self.config.vessel_descs, self.config.colreg_situation_descs) 
        else:
            raise Exception('unknown parameter')
            
        self.vessels, self.colreg_situations = self.initializer.get_one_population_as_objects()        
        self.smallest_ship = min(self.vessels, key=lambda v: v.r)
        self.largest_ship = max(self.vessels, key=lambda v: v.r)
        self.xl, self.xu = self.generate_gene_space()
        
    def update(self, states : List[float]):
        if len(states) != self.config.all_variable_num:
            raise Exception("the variable number is insufficient.")
        
        states = OWN_VESSEL_STATES + states
        for vessel in self.vessels:
            vessel.update(states[vessel.id * VARIABLE_NUM],
                                states[vessel.id * VARIABLE_NUM + 1],
                                states[vessel.id * VARIABLE_NUM + 2],
                                states[vessel.id * VARIABLE_NUM + 3])
            
        for colreg_situation in self.colreg_situations:
            colreg_situation.update()
            
        return self
         
    @staticmethod  
    def euler_distance(fitness : List[float]):
        return math.sqrt(sum([x**2 for x in fitness]))
          
          
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
        xl = [self.config.vessel_descs[0].min_speed]
        xu = [self.config.vessel_descs[0].max_speed]
        for vessel_desc in self.config.vessel_descs[1:]:
            xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel_desc.min_speed]
            xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel_desc.max_speed]
        return xl, xu