import random
from typing import List
import numpy as np
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING
from abc import ABC, abstractmethod
from logical_level.model.vessel_variable import VesselVariable

class InstanceInitializer(ABC):    
    def __init__(self, name: str, vessel_vars : List[VesselVariable]) -> None:
        self.vessel_vars = vessel_vars      
        self.name = name
       
    @abstractmethod     
    def get_population(self, pop_size) -> List[List[float]]:
        pass
class RandomInstanceInitializer(InstanceInitializer):
    name = 'uniform'
    def __init__(self, vessel_vars : List[VesselVariable]) -> None:
        super().__init__(self.name, vessel_vars)
        
    def get_population(self, pop_size) -> List[List[float]]:
        result : List[List[float]] = []
        for i in range(int(pop_size)):
            population : List[float] = [random.uniform(self.vessel_vars[0].min_length, self.vessel_vars[0].max_length), 
                                        random.uniform(self.vessel_vars[0].min_speed, self.vessel_vars[0].max_speed)]
            for vessel_var in self.vessel_vars[1:]:
                group = [random.uniform(MIN_COORD, MAX_COORD),
                        random.uniform(MIN_COORD, MAX_COORD),
                        random.uniform(MIN_HEADING, MAX_HEADING),
                        random.uniform(vessel_var.min_length, vessel_var.max_length),
                        random.uniform(vessel_var.min_speed, vessel_var.max_speed)]
                population.extend(group)
            result.append(population)
        return result  
    
    
    
class DeterministicInitializer(InstanceInitializer):
    name = 'deterministic'
    def __init__(self, vessel_vars : List[VesselVariable]) -> None:
        super().__init__(self.name, vessel_vars)
        
    def get_population(self, pop_size) -> List[List[float]]:
        result : List[List[float]] = []
        for i in range(int(pop_size)):
            population : List[float] = [(self.vessel_vars[0].min_length + self.vessel_vars[0].max_length) / 2.0,
                                        (self.vessel_vars[0].min_speed + self.vessel_vars[0].max_speed) / 2.0]
            for vessel_var in self.vessel_vars[1:]:
                group = [MAX_COORD / 2, MAX_COORD / 2, 0, 
                         (vessel_var.min_length + vessel_var.max_length) / 2,
                         (vessel_var.min_speed + vessel_var.max_speed) / 2]
                population.extend(group)
            result.append(population)
        return result 
    

class LatinHypercubeInitializer(InstanceInitializer):
    name = 'lhs'
    def __init__(self, vessel_vars : List[VesselVariable]) -> None:
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

    def get_population(self, pop_size: int) -> List[List[float]]:
        result: List[List[float]] = []
        
        # Prepare bounds for each vessel parameter using LHS
        for i in range(int(pop_size)):
            population: List[float] = []
            
            # First vessel (speed only)
            first_length = self.lhs_sampling(1, [self.vessel_vars[0].min_length], [self.vessel_vars[0].max_length])[0]
            population.extend(first_length)
            first_speed = self.lhs_sampling(1, [self.vessel_vars[0].min_speed], [self.vessel_vars[0].max_speed])[0]
            population.extend(first_speed)

            # Subsequent vessels (coordinate, heading, and speed)
            for vessel_var in self.vessel_vars[1:]:
                lower_bounds = [MIN_COORD, MIN_COORD, MIN_HEADING, vessel_var.min_length, vessel_var.min_speed]
                upper_bounds = [MAX_COORD, MAX_COORD, MAX_HEADING, vessel_var.max_length, vessel_var.max_speed]
                
                # LHS for this vessel's parameters
                group = self.lhs_sampling(1, lower_bounds, upper_bounds)[0]
                population.extend(group)

            result.append(population)

        return result 
    
    