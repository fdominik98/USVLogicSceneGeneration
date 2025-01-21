from typing import List
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.logical_scenario import LogicalScenario
from abc import ABC, abstractmethod
import numpy as np
from logical_level.models.penalty import Penalty

class Aggregate(ABC):
    name = 'unspecified'
    
    def __init__(self, logical_scenario : LogicalScenario, minimize : bool):
        super().__init__()
        self.logical_scenario = logical_scenario
        self.minimize = minimize
        
    @property
    def sign(self):
        return 1.0 if self.minimize else -1.0
    
    @property
    @abstractmethod
    def object_num(self) -> int:
        pass
        
    @abstractmethod    
    def evaluate(self, individual : np.ndarray):
        pass
    
    def derive_penalty(self, individual : np.ndarray) -> Penalty :
        assignments = Assignments(self.logical_scenario.actor_vars).update_from_individual(individual)
        penalty = self.logical_scenario.relation_constraint.evaluate_penalty(assignments)
        return penalty
    
    def _signed_penalty(self, penalty) -> float:
        return self.sign * abs(penalty)
     
    @staticmethod
    def factory(logical_scenario : LogicalScenario, name : str, minimize):
        if name == ActorAggregate.name:
            return ActorAggregate(logical_scenario, minimize)      
        elif name == AggregateAll.name:
            return AggregateAll(logical_scenario, minimize)     
        elif name == AggregateAllSwarm.name:
            return AggregateAllSwarm(logical_scenario, minimize)      
        elif name == CategoryAggregate.name:
            return CategoryAggregate(logical_scenario, minimize)         
        else:
            raise Exception('Unknown aggregate')

class ActorAggregate(Aggregate):
    name = 'actor'
    
    def __init__(self, logical_scenario : LogicalScenario, minimize):
        super().__init__(logical_scenario, minimize)
    
    @property
    def object_num(self) -> int:
        return int(self.logical_scenario.size)

    def evaluate(self, individual : np.ndarray):
        penalty = self.derive_penalty(individual)
        return tuple((penalty.actor_penalties[var] for var in self.logical_scenario.actor_vars))
    
class AggregateAll(Aggregate):
    name =  'all'
    
    def __init__(self, logical_scenario : LogicalScenario, minimize):
        super().__init__(logical_scenario, minimize)
        
    @property
    def object_num(self) -> int:
        return 1

    def evaluate(self, individual : np.ndarray):
        fitness = self._signed_penalty(self.derive_penalty(individual).total_penalty)
        return (fitness, )
    
class AggregateAllSwarm(AggregateAll):
    name = 'all_swarm'
    
    def __init__(self, logical_scenario : LogicalScenario, minimize):
        super().__init__(logical_scenario, minimize)
        
    def evaluate(self, individual : np.ndarray):
        fitnesses : List[float] = []
        for particle in individual:
            fitnesses.append(super().evaluate(particle)[0])
        return np.array(fitnesses)
    
    
class CategoryAggregate(Aggregate):
    name = 'category'
    
    def __init__(self, logical_scenario, minimize):
        super().__init__(logical_scenario, minimize)
        
    @property
    def object_num(self) -> int:
        return Penalty.category_num

    def evaluate(self, individual : np.ndarray):
        penalty = self.derive_penalty(individual)
        return tuple((self._signed_penalty(pen) for pen in penalty.categorical_penalties))
   