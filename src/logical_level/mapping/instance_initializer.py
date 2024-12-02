import random
from typing import Dict, List
import numpy as np
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING
from model.vessel import VesselDesc
from model.relation import Relation, RelationClause, RelationDescClause
from abc import ABC, abstractmethod
from logical_level.model.vessel_variable import VesselVariable
from logical_level.constraint_satisfaction.assignments import Assignments

class InstanceInitializer(ABC):    
    def __init__(self, vessel_descs : List[VesselDesc], relation_desc_clauses : List[RelationDescClause]) -> None:
        vessels: Dict[VesselDesc, VesselVariable] = {vessel_desc : VesselVariable(vessel_desc) for vessel_desc in vessel_descs}
        self.assignments = Assignments(list(vessels.values()))
        self.vessel_vars = list(self.assignments.keys())
        
        for relation_desc_clause in relation_desc_clauses:
            clause = RelationClause()
            for relation_desc in relation_desc_clause.relation_descs:
                vd1 = relation_desc.vd1
                vd2 = relation_desc.vd2
                clause.append(Relation(vessels[vd1], relation_desc.relation_types, vessels[vd2]))
            self.assignments.register_clause(clause)    
        
       
    @abstractmethod     
    def get_population(self, pop_size) -> List[List[float]]:
        pass
class RandomInstanceInitializer(InstanceInitializer):
    def __init__(self, vessel_descs : List[VesselDesc], relation_descs : List[RelationDescClause]) -> None:
        super().__init__(vessel_descs, relation_descs)
        
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
    def __init__(self, vessel_descs : List[VesselDesc], relation_descs : List[RelationDescClause]) -> None:
        super().__init__(vessel_descs, relation_descs)
        
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
    def __init__(self, vessel_descs : List[VesselDesc], relation_descs : List[RelationDescClause]) -> None:
        super().__init__(vessel_descs, relation_descs)
        
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
    
    