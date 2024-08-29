import math
from model.instance_initializer import RandomInstanceInitializer, DeterministicInitializer
from model.usv_environment_desc import USVEnvironmentDesc
from model.usv_config import OWN_VESSEL_STATES, VARIABLE_NUM


class USVEnvironment():
    def __init__(self, env_config : USVEnvironmentDesc) -> None:
        self.config = env_config
        self.initializer = RandomInstanceInitializer(self.config.vessel_descs, self.config.colreg_situation_descs) 
        self.vessels, self.colreg_situations = self.initializer.get_one_population_as_objects()
        
        self.smallest_ship = min(self.vessels, key=lambda v: v.l)
        self.largest_ship = max(self.vessels, key=lambda v: v.l)
        
    def update(self, states : list[float]):
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
    
    def evaluate(self, states : list[float]):
        self.update(states)
        penalties = []
        for colreg_situation in self.colreg_situations: 
            penalties += colreg_situation.penalties()[1]
        return self.euler_distance(penalties)
        
    @staticmethod  
    def euler_distance(fitness : list[float]):
        return math.sqrt(sum([x**2 for x in fitness]))
          
          
    def get_population(self, pop_size) -> list[list[float]]:
        population = self.initializer.get_population(pop_size=pop_size)
        return population
    