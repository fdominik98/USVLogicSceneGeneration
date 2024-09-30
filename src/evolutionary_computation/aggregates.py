from typing import List
from model.environment.usv_environment import USVEnvironment
from abc import ABC, abstractmethod
import numpy as np

class Aggregate(ABC):
    
    def __init__(self, env : USVEnvironment, name : str, minimize) -> None:
        super().__init__()
        self.env = env
        self.obj_num = self._get_object_num()
        self.minimize = minimize
        self.sign = 1.0 if minimize else -1.0
        self.weights= (-self.sign,) * self.obj_num 
        self.name = name
        
    @abstractmethod    
    def evaluate(self, individual : np.ndarray):
        pass
    
    @abstractmethod
    def _get_object_num(self) -> int:
        pass
    
    def _get_penalty(self, penalty) -> float:
         if penalty <= 0:
            return 0
         return self.sign * penalty

        
class VesselAggregate(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, 'vessel', minimize)
        
    def _get_object_num(self):
        return int(self.env.config.actor_num)

    def evaluate(self, individual : np.ndarray):
        self.env.update(individual.tolist())
        return self.loose_evaluate() 
   
    
    def loose_evaluate(self):
        objectives = [0] * self._get_object_num()      
        for rel in self.env.relations:
            for rel_type in rel.relations:
                penalty = rel_type.get_penalty_norm() 
                objectives[rel.vessel1.id] += self._get_penalty(penalty)
                objectives[rel.vessel2.id] += self._get_penalty(penalty)
        
        return tuple(objectives)
    
    
class AggregateAll(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, 'all', minimize)
        
    def _get_object_num(self) -> int:
        return 1

    def evaluate(self, individual : np.ndarray):
        self.env.update(individual.tolist())       
        return (self.loose_evaluate(), )
    
    def loose_evaluate(self):
        fitness = 0.0
        for rel in self.env.relations:
            for rel_type in rel.relations:
                penalty = rel_type.get_penalty_norm()
                fitness += self._get_penalty(penalty)
        return fitness
        
    
class AggregateAllSwarm(AggregateAll):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def evaluate(self, individual : np.ndarray):
        fitnesses : List[float] = []
        for particle in individual:
            fitnesses.append(super().evaluate(particle)[0])
        return np.array(fitnesses)
    
    
    
class CategoryAggregate(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, 'category', minimize)
        
    def _get_object_num(self):
        return 3

    def evaluate(self, individual : np.ndarray):
        self.env.update(individual.tolist())
        return self.loose_evaluate() 
   
    
    def loose_evaluate(self):
        objectives = [0] * self._get_object_num()      
        for rel in self.env.relations:
            for rel_type in rel.collision_relations:
                penalty = rel_type.get_penalty_norm() 
                objectives[0] += self._get_penalty(penalty)
            for rel_type in rel.visibility_relations:
                penalty = rel_type.get_penalty_norm() 
                objectives[1] += self._get_penalty(penalty)
            for rel_type in rel.bearing_relations:
                penalty = rel_type.get_penalty_norm() 
                objectives[2] += self._get_penalty(penalty)
        
        return tuple(objectives)