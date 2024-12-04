from typing import List
from logical_level.models.logical_scenario import LogicalScenario
from abc import ABC, abstractmethod
import numpy as np

class Aggregate(ABC):
    
    def __init__(self,logical_scenario: LogicalScenario, name : str, minimize) -> None:
        super().__init__()
        self.logical_scenario = env
        self.obj_num = self._get_object_num()
        self.minimize = minimize
        self.sign = 1.0 if minimize else -1.0
        self.name = name
        
    @abstractmethod    
    def evaluate(self, individual : np.ndarray):
        pass
    
    @abstractmethod
    def _get_object_num(self) -> int:
        pass
    
    def _signed_penalty(self, penalty) -> float:
        return self.sign * abs(penalty)
     
    @staticmethod
    def factory(env : LogicalScenario, name : str, minimize = False):
        if name == 'vessel':
            return VesselAggregate(logical_scenario, minimize=minimize, name='vessel')      
        elif name == 'all':
            return AggregateAll(logical_scenario, minimize=minimize, name='all')     
        elif name == 'all_swarm':
            return AggregateAllSwarm(logical_scenario, minimize=minimize, name='all_swarm')      
        elif name == 'category':
            return CategoryAggregate(logical_scenario, minimize=minimize, name='category')         
        else:
            raise Exception('Unknown aggregate')

        
class VesselAggregate(Aggregate):
    def __init__(self,logical_scenario: LogicalScenario, minimize=False, name = 'vessel') -> None:
        super().__init__(logical_scenario, name, minimize)
        
    def _get_object_num(self):
        return int(self.logical_scenario.config.vessel_num)

    def evaluate(self, individual : np.ndarray):
        self.logical_scenario.update(individual.tolist())
        return self.loose_evaluate() 
   
    
    def loose_evaluate(self):
        objectives = [0] * self._get_object_num()      
        for rel in self.logical_scenario.relations:
            objectives[rel.vessel1.id] += self._signed_penalty(rel.penalties_sum)
            objectives[rel.vessel2.id] += self._signed_penalty(rel.penalties_sum)
        
        return tuple(objectives)
    
    
class AggregateAll(Aggregate):
    def __init__(self,logical_scenario: LogicalScenario, minimize=False, name = 'all') -> None:
        super().__init__(logical_scenario, name, minimize)
        
    def _get_object_num(self) -> int:
        return 1

    def evaluate(self, individual : np.ndarray):
        self.logical_scenario.update(individual.tolist())       
        return (self.loose_evaluate(), )
    
    def loose_evaluate(self):
        fitness = self._signed_penalty(self.logical_scenario.clause.penalties_sum)
        return fitness
        
    
class AggregateAllSwarm(AggregateAll):
    def __init__(self,logical_scenario: LogicalScenario, minimize=False, name = 'all_swarm') -> None:
        super().__init__(logical_scenario, minimize, name)
        
    def evaluate(self, individual : np.ndarray):
        fitnesses : List[float] = []
        for particle in individual:
            fitnesses.append(super().evaluate(particle)[0])
        return np.array(fitnesses)
    
    
    
class CategoryAggregate(Aggregate):
    def __init__(self,logical_scenario: LogicalScenario, minimize=False, name = 'category') -> None:
        super().__init__(logical_scenario, name, minimize)
        
    def _get_object_num(self):
        return 3

    def evaluate(self, individual : np.ndarray):
        self.logical_scenario.update(individual.tolist())
        return self.loose_evaluate() 
   
    
    def loose_evaluate(self):
        objectives = self.logical_scenario.clause.category_penalties
        return tuple(objectives)