from dataclasses import dataclass, field
from typing import List
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.logical_scenario import LogicalScenario
from abc import ABC, abstractmethod
import numpy as np
from logical_level.models.penalty import Penalty

dataclass(frozen=True)
class Aggregate(ABC):
    logical_scenario : LogicalScenario
    minimize : bool
    name : str
        
    @property
    def sign(self):
        return 1.0 if self.minimize else -1.0
    
    @abstractmethod
    @property
    def obj_num(self) -> int:
        pass
        
    @abstractmethod    
    def evaluate(self, individual : np.ndarray):
        pass
    
    def derive_penalty(self, individual : np.ndarray) -> Penalty :
        assignments = Assignments(self.logical_scenario.actor_vars).update_from_individual(individual)
        penalty = self.logical_scenario.relation_constr_clause.evaluate_penalty(assignments)
        return penalty
    
    def _signed_penalty(self, penalty) -> float:
        return self.sign * abs(penalty)
     
    @staticmethod
    def factory(logical_scenario : LogicalScenario, name : str, minimize):
        if name == VesselAggregate.name:
            return VesselAggregate(logical_scenario, minimize)      
        elif name == AggregateAll.name:
            return AggregateAll(logical_scenario, minimize)     
        elif name == AggregateAllSwarm.name:
            return AggregateAllSwarm(logical_scenario, minimize)      
        elif name == CategoryAggregate.name:
            return CategoryAggregate(logical_scenario, minimize)         
        else:
            raise Exception('Unknown aggregate')

@dataclass(frozen=True)    
class VesselAggregate(Aggregate):
    name : str = field(default='vessel', init=False)
    
    @property
    def object_num(self) -> int:
        return int(self.logical_scenario.actor_num)

    def evaluate(self, individual : np.ndarray):
        penalty = self.derive_penalty(individual)
        return (penalty.actor_penalties[var] for var in self.logical_scenario.actor_vars) 
    
@dataclass(frozen=True)
class AggregateAll(Aggregate):
    name : str = field(default='all', init=False)
        
    @property
    def object_num(self) -> int:
        return 1

    def evaluate(self, individual : np.ndarray):
        fitness = self._signed_penalty(self.derive_penalty(individual).total_penalty)
        return (fitness, )
    
@dataclass(frozen=True)
class AggregateAllSwarm(AggregateAll):
    name : str = field(default='all_swarm', init=False)
        
    def evaluate(self, individual : np.ndarray):
        fitnesses : List[float] = []
        for particle in individual:
            fitnesses.append(super().evaluate(particle)[0])
        return np.array(fitnesses)
    
    
@dataclass(frozen=True)
class CategoryAggregate(Aggregate):
    name : str = field(default='category', init=False)
        
    @property
    def object_num(self) -> int:
        return 3

    def evaluate(self, individual : np.ndarray):
        penalty = self.derive_penalty(individual)
        return (self._signed_penalty(pen) for pen in penalty.total_categorical_penalties)
   