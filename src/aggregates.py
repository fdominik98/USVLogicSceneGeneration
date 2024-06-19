from model.usv_environment import USVEnvironment
from model.usv_config import *
from abc import ABC, abstractmethod


class Aggregate(ABC):
    def __init__(self, env : USVEnvironment, minimize) -> None:
        super().__init__()
        self.env = env
        self.obj_num = self._get_object_num()
        self.minimize = minimize
        self.sign = 1.0 if minimize else -1.0
        self.weights= (-self.sign,) * self.obj_num 
        
    @abstractmethod    
    def evaluate(self, individual):
        pass
    
    @abstractmethod
    def _get_object_num(self) -> int:
        pass


class ConstraintClassAggregate(Aggregate):    
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def _get_object_num(self) -> int:
        return int(constraint_number)
    
    def evaluate(self, individual):
        self.env.update(individual)
        
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
        return int(constraint_number * self.env.config.col_sit_num)

    def evaluate(self, individual):
        self.env.update(individual)
        
        objectives : list = []
        for colreg_sit in self.env.colreg_situations:
            for penalty in colreg_sit.penalties:
                if penalty <= 0:
                    objectives.append(0)
                else:
                    objectives.append(self.sign * penalty) 
        return tuple(objectives)
    

class PenaltyClassAggregate(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def _get_object_num(self) -> int:
        return int((constraint_number * self.env.config.col_sit_num) / 2)

    def evaluate(self, individual):
        self.env.update(individual)
        
        objectives : list = []
        for colreg_sit in self.env.colreg_situations:
            for i, penalty in enumerate(colreg_sit.penalties):
                if penalty <= 0:
                    penalty = 0
                else:
                    penalty = self.sign * penalty
                if i % 2 == 0:
                    objectives.append(penalty)
                else:
                    objectives[-1] = objectives[-1] + penalty 
        return tuple(objectives)
    
    
class AggregateAll(Aggregate):
    def __init__(self, env : USVEnvironment, minimize=False) -> None:
        super().__init__(env, minimize)
        
    def _get_object_num(self) -> int:
        return 1

    def evaluate(self, individual):
        self.env.update(individual)       
        
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

    def evaluate(self, individual):
        return (self.sign * self.env.evaluate(individual),)