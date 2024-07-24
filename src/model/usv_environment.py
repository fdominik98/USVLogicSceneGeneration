from model.usv_config import boundaries, max_distance
from model.vessel import Vessel
import math
from model.instance_initializer import InstanceInitializer
from model.usv_environment_config import USVEnvironmentConfig
import random
from model.colreg_situation import ColregSituation

class USVEnvironment():
    def __init__(self, env_config : USVEnvironmentConfig) -> None:
        self.config = env_config
        self.max_distance = max_distance(self.config.actor_num)                 
        self.initializer = InstanceInitializer(self.config.radii, self.config.colreg_situations) 
        self.vessels, self.colreg_situations = self.convert_population_to_objects(self.get_random_population(1)[0])  
        
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
        population = self.initializer.get_population(num=pop_size)
        result : list[list[float]] = []
        for vessels, _ in population:
            result.append([])
            for vessel in vessels:
                result[-1] += [vessel.p[0], vessel.p[1], vessel.v[0], vessel.v[1]]
        return result
    
    def get_random_population(self, pop_size) -> list[list[float]]:
        result : list[list[float]] = []
        for i in range(int(pop_size)):
            population : list[float] = []
            for j in range(self.config.actor_num):
                group = [random.uniform(boundary[0], boundary[1]) for boundary in boundaries(self.config.actor_num)]
                population.extend(group)
            result.append(population)
        return result
    
    
    def convert_population_to_objects(self, states: list[float]) -> tuple[list[Vessel], set[ColregSituation]]:
        vessels = self.generate_vessels(self.config)
        for i, vessel in enumerate(vessels):
            vessel.update(states[i * 4], states[i * 4 + 1], states[i * 4 + 2], states[i * 4 + 3])
            
        colreg_situations : set[ColregSituation] = set()        
        for colreg_situation in self.config.colreg_situations:
            colreg_situations.add(colreg_situation.colreg_class(vessels[colreg_situation.id1],
                                    vessels[colreg_situation.id2], colreg_situation.distance, self.max_distance))
        return vessels, colreg_situations 
            
         
    @staticmethod   
    def generate_vessels(env_config : USVEnvironmentConfig) -> list[Vessel]:
        vessels = []
        for id, radius in enumerate(env_config.radii):
            vessels.append(Vessel(id, radius))
        return vessels