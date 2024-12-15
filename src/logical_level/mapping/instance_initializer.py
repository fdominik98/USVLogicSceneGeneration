import random
from typing import List
import numpy as np
from abc import ABC, abstractmethod
from logical_level.models.actor_variable import ActorVariable

class InstanceInitializer(ABC):    
    def __init__(self, name: str, vessel_vars : List[ActorVariable]) -> None:
        self.actor_vars = vessel_vars      
        self.name = name
       
    @abstractmethod     
    def _do_get_population(self) -> List[float]:
        pass
    
    def get_population(self, pop_size) -> List[List[float]]:
        result : List[List[float]] = []
        for i in range(int(pop_size)):
            result.append(self._do_get_population())
        return result
class RandomInstanceInitializer(InstanceInitializer):
    name = 'uniform'
    def __init__(self, vessel_vars : List[ActorVariable]) -> None:
        super().__init__(self.name, vessel_vars)
        
    def _do_get_population(self) -> List[float]:
        population : List[float] = []
        for vessel_var in self.actor_vars:
            population += [random.uniform(x, y) for x, y in zip(vessel_var.lower_bounds, vessel_var.upper_bounds)]                
        return population
    
    
class DeterministicInitializer(InstanceInitializer):
    name = 'deterministic'
    def __init__(self, vessel_vars : List[ActorVariable]) -> None:
        super().__init__(self.name, vessel_vars)
        
    def _do_get_population(self) -> List[float]:
        population : List[float] = []
        for vessel_var in self.actor_vars:
            population += [(x + y) / 2 for x, y in zip(vessel_var.lower_bounds, vessel_var.upper_bounds)]                
        return population 
    

class LatinHypercubeInitializer(InstanceInitializer):
    name = 'lhs'
    def __init__(self, vessel_vars : List[ActorVariable]) -> None:
        super().__init__(self.name, vessel_vars)
        
    def lhs_sampling(self, n_samples: int, lower_bounds: List[float], upper_bounds: List[float]) -> np.ndarray:
        """
        Generate Latin Hypercube samples within specified bounds for each dimension.
        
        :param n_samples: Number of samples to generate.
        :param lower_bounds: List of lower bounds for each dimension.
        :param upper_bounds: List of upper bounds for each dimension.
        :return: Array of Latin Hypercube samples.
        """
        n_dim = len(lower_bounds)
        result = np.zeros((n_samples, n_dim))
        
        # Create intervals for each dimension
        intervals = np.linspace(0, 1, n_samples + 1)
        
        for i in range(n_dim):
            points = np.random.uniform(intervals[:-1], intervals[1:])
            np.random.shuffle(points)  # Ensure random ordering of points in this dimension
            result[:, i] = lower_bounds[i] + points * (upper_bounds[i] - lower_bounds[i])
        
        return result

    def _do_get_population(self) -> List[float]:
        population: List[float] = []
        for vessel_var in self.actor_vars:
            population += self.lhs_sampling(1, vessel_var.lower_bounds, vessel_var.upper_bounds)[0]
        return population
    
    