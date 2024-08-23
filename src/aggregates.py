from model.usv_environment import USVEnvironment
from abc import ABC, abstractmethod
from model.usv_config import CONSTRAINT_NUMBER, MIN_SPEED, interval_penalty
import numpy as np

class Aggregate(ABC):
    
    precedence = [
        1,
        1,
        10e6,
        10e6
    ]
    
    def __init__(self, env : USVEnvironment, minimize) -> None:
        super().__init__()
        self.env = env
        self.obj_num = self._get_object_num()
        self.minimize = minimize
        self.sign = 1.0 if minimize else -1.0
        self.weights= (-self.sign,) * self.obj_num 
        
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


class ConstraintClassAggregate(Aggregate):    
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def _get_object_num(self) -> int:
        return int(CONSTRAINT_NUMBER)
    
    def evaluate(self, individual : np.ndarray):
        self.env.update(individual.tolist())
        
        objectives = [0,] * self.obj_num
        for colreg_sit in self.env.colreg_situations:
            for i, penalty in enumerate(colreg_sit.penalties):   
                if penalty > 0.0:
                    objectives[i] += self.sign * penalty
        return tuple(objectives)
    
    
class NoAggregate(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def _get_object_num(self):
        return int(CONSTRAINT_NUMBER * self.env.config.col_sit_num)

    def evaluate(self, individual):
        self.env.update(individual.tolist())
        objectives : list = []
        
        for colreg_sit in self.env.colreg_situations:
            for penalty in colreg_sit.penalties:
                objectives.append(self._get_penalty(penalty))
        return tuple(objectives)
    
class VesselAggregate(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def _get_object_num(self):
        return int(self.env.config.actor_num)

    def evaluate(self, individual : np.ndarray):
        self.env.update(individual.tolist())
        objectives = [0] * self._get_object_num()
      
        for colreg_sit in self.env.colreg_situations:
            for i, penalty in enumerate(colreg_sit.penalties):
                objectives[colreg_sit.vessel1.id] += self._get_penalty(penalty * self.precedence[i])
                objectives[colreg_sit.vessel2.id] += self._get_penalty(penalty * self.precedence[i])
        
        return tuple(objectives)
    
   
class AggregateAll(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def _get_object_num(self) -> int:
        return 1

    def evaluate(self, individual : np.ndarray):
        self.env.update(individual.tolist())       
        
        fitness = 0.0
        for colreg_sit in self.env.colreg_situations:
            for penalty in colreg_sit.penalties:
                if penalty > 0.0:
                    fitness += self.sign * penalty
        return (fitness,)
    
class EulerDistance(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def _get_object_num(self) -> int:
        return 1

    def evaluate(self, individual : np.ndarray):
        return (self.sign * self.env.evaluate(individual.tolist()),)