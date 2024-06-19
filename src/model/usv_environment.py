from model.usv_config import *
from model.vessel import Vessel
import math
from model.instance_initializer import InstanceInitializer
from model.usv_environment_config import USVEnvironmentConfig

class USVEnvironment():
    def __init__(self, env_config : USVEnvironmentConfig) -> None:
        self.config = env_config
        self.initializer = InstanceInitializer(self.config.radii, self.config.colreg_situations) 
        self.vessels, self.colreg_situations = self.initializer.get_population(num=1)[0]                   
            
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
          
    def get_population(self, pop_size):
        population = self.initializer.get_population(num=pop_size)
        result : list[list[float]] = []
        for vessels, _ in population:
            result.append([])
            for vessel in vessels:
                result[-1] += [vessel.p[0], vessel.p[1], vessel.v[0], vessel.v[1]]
        return result
         
    @staticmethod   
    def generate_vessels(env_config : USVEnvironmentConfig):
        vessels = []
        for id, radius in enumerate(env_config.radii):
            vessels.append(Vessel(id, radius))
        return vessels