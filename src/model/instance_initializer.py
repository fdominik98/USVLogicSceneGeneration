import random
from typing import Dict, List, Tuple
import numpy as np
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING, OWN_VESSEL_STATES, VARIABLE_NUM
from model.vessel import Vessel, VesselDesc
from model.relation import Relation, RelationClause, RelationDescClause
from abc import ABC, abstractmethod

class InstanceInitializer(ABC):    
    def __init__(self, vessel_descs : List[VesselDesc], relation_desc_clauses : List[RelationDescClause]) -> None:
        self.vessel_descs = vessel_descs
        self.actor_num = len(vessel_descs)
        self.relation_desc_clauses = relation_desc_clauses
       
    @abstractmethod     
    def get_population(self, pop_size) -> List[List[float]]:
        pass

    def convert_population_to_objects(self, states: List[float]) -> Tuple[List[Vessel], List[RelationClause]]:
        states = OWN_VESSEL_STATES + states
        vessels: Dict[int, Vessel] = {}
        for vessel_desc in self.vessel_descs:
            vessel = Vessel(vessel_desc)
            vessel.update(states[vessel.id * VARIABLE_NUM],
                            states[vessel.id * VARIABLE_NUM + 1],
                            states[vessel.id * VARIABLE_NUM + 2],
                            states[vessel.id * VARIABLE_NUM + 3])
            vessels[vessel.id] = vessel
            
        relation_clauses : List[RelationClause] = []     
        for relation_desc_clause in self.relation_desc_clauses:
            clause = RelationClause()
            for relation_desc in relation_desc_clause.relation_descs:
                vd1 = relation_desc.vd1
                vd2 = relation_desc.vd2
                clause.append(Relation(vessels[vd1.id], relation_desc.relation_types, vessels[vd2.id]))
            relation_clauses.append(clause)
        return list(vessels.values()), relation_clauses
    
    
    def get_one_population_as_objects(self) -> Tuple[List[Vessel], List[RelationClause]]:
        return self.convert_population_to_objects(self.get_population(1)[0])
    
class RandomInstanceInitializer(InstanceInitializer):
    def __init__(self, vessel_descs : List[VesselDesc], relation_descs : List[RelationDescClause]) -> None:
        super().__init__(vessel_descs, relation_descs)
        
    def get_population(self, pop_size) -> List[List[float]]:
        result : List[List[float]] = []
        for i in range(int(pop_size)):
            population : List[float] = [random.uniform(self.vessel_descs[0].min_speed, self.vessel_descs[0].max_speed)]
            for vessel_desc in self.vessel_descs[1:]:
                group = [random.uniform(MIN_COORD, MAX_COORD),
                        random.uniform(MIN_COORD, MAX_COORD),
                        random.uniform(MIN_HEADING, MAX_HEADING),
                        random.uniform(vessel_desc.min_speed, vessel_desc.max_speed)]
                population.extend(group)
            result.append(population)
        return result  
    
    
    
class DeterministicInitializer(InstanceInitializer):
    def __init__(self, vessel_descs : List[VesselDesc], relation_descs : List[RelationDescClause]) -> None:
        super().__init__(vessel_descs, relation_descs)
        
    def get_population(self, pop_size) -> List[List[float]]:
        result : List[List[float]] = []
        for i in range(int(pop_size)):
            population : List[float] = [(self.vessel_descs[0].min_speed + self.vessel_descs[0].max_speed) / 2.0]
            for vessel_desc in self.vessel_descs[1:]:
                group = [MAX_COORD / 2, MAX_COORD / 2, 0, (vessel_desc.min_speed + vessel_desc.max_speed) / 2]
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
            first_speed = self.lhs_sampling(1, [self.vessel_descs[0].min_speed], [self.vessel_descs[0].max_speed])[0]
            population.extend(first_speed)

            # Subsequent vessels (coordinate, heading, and speed)
            for vessel_desc in self.vessel_descs[1:]:
                lower_bounds = [MIN_COORD, MIN_COORD, MIN_HEADING, vessel_desc.min_speed]
                upper_bounds = [MAX_COORD, MAX_COORD, MAX_HEADING, vessel_desc.max_speed]
                
                # LHS for this vessel's parameters
                group = self.lhs_sampling(1, lower_bounds, upper_bounds)[0]
                population.extend(group)

            result.append(population)

        return result 
    
    