import math
from typing import List
from model.instance_initializer import RandomInstanceInitializer, DeterministicInitializer
from model.usv_environment_desc import USVEnvironmentDesc
from model.usv_config import OWN_VESSEL_STATES, VARIABLE_NUM


class USVEnvironment():
    def __init__(self, env_config : USVEnvironmentDesc) -> None:
        self.config = env_config
        self.initializer = RandomInstanceInitializer(self.config.vessel_descs, self.config.colreg_situation_descs) 
        self.vessels, self.colreg_situations = self.initializer.get_one_population_as_objects()
        
        self.smallest_ship = min(self.vessels, key=lambda v: v.r)
        self.largest_ship = max(self.vessels, key=lambda v: v.r)
        
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
    
    def get_vessel_by_id(self, id):
        vessel = next((v for v in self.vessels if v.id == id), None)
        if vessel is None:
            raise Exception(f"No vessel with id {id}")
        return vessel
    