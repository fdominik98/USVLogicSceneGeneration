from scipy.optimize import differential_evolution, OptimizeResult

# Define your objectives
def objective(x, weights=[0.5, 0.5]):
    f1 = x[0]**2 + x[1]**2
    f2 = (x[0] - 2)**2 + (x[1] - 1)**2
    return weights[0] * f1 + weights[1] * f2

bounds = [(-5, 5), (-5, 5)]

# Use different weight combinations for different Pareto solutions



import time
from typing import List, Tuple

import numpy as np
from evolutionary_computation.aggregates import Aggregate, AggregateAll, AggregateAllSwarm
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import GeneticAlgorithmBase

from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING

class PciPyDEAlgorithm(GeneticAlgorithmBase):
    
    def __init__(self, measurement_name : str, config_name: str, verbose : bool, random_init : bool = True, runtime : int = 300) -> None:
        super().__init__(measurement_name, 'scipy_DE_algorithm', config_name, verbose, random_init, runtime)
    
    def get_aggregate(self, env) -> Aggregate:
        return AggregateAll(env, minimize=True)   
    
    
    def init_problem(self, initial_population : List[List[float]], eval_data : EvaluationData):
        lb, ub = self.generate_gene_space()
    
    def do_evaluate(self, some_input, eval_data : EvaluationData):
       return differential_evolution(objective, bounds, args=([0.7, 0.3],))
    
    def convert_results(self, some_results : OptimizeResult, eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
       print(some_results)

    # Attribute generator with different boundaries
    def generate_gene_space(self):
        xl = [self.env.config.vessel_descs[0].min_speed]
        xu = [self.env.config.vessel_descs[0].max_speed]
        for vessel_desc in self.env.config.vessel_descs[1:]:
            xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel_desc.min_speed]
            xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel_desc.max_speed]
        return xl, xu


    

