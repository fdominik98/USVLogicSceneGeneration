from model.usv_config import MAX_DISTANCE
import math
from model.random_instance_initializer import RandomInstanceInitializer
from model.usv_environment_desc import USVEnvironmentDesc

class USVEnvironment():
    def __init__(self, env_config : USVEnvironmentDesc) -> None:
        self.config = env_config
        self.max_distance = MAX_DISTANCE(self.config.actor_num)                 
        self.initializer = RandomInstanceInitializer(self.config.vessel_descs, self.config.colreg_situation_descs) 
        self.vessels, self.colreg_situations = self.initializer.get_one_population_as_objects()
        
    def update(self, states : list[float]):
        if len(states) != len(self.vessels) * 4:
            raise Exception("the variable number is insufficient.")
        for i in range(len(self.vessels)):
            self.vessels[i].update(states[i * 4], states[i * 4 + 1], states[i * 4 + 2], states[i * 4 + 3])
        for colreg_situation in self.colreg_situations:
            colreg_situation.update()
            
        return self
    
    def evaluate(self, states : list[float]):
        self.update(states)
        penalties = []
        for colreg_situation in self.colreg_situations: 
            penalties += colreg_situation.penalties
        return self.euler_distance(penalties)
        
    @staticmethod  
    def euler_distance(fitness : list[float]):
        return math.sqrt(sum([x**2 for x in fitness]))
          
          
    def get_population(self, pop_size) -> list[list[float]]:
        population = self.initializer.get_population(pop_size=pop_size)
        return population
    