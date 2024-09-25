import time
from typing import List, Tuple
import numpy as np
from evolutionary_computation.aggregates import AggregateAllSwarm
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import GeneticAlgorithmBase
import pyswarms as ps
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.environment.usv_environment import USVEnvironment

class PySwarmPSOAlgorithm(GeneticAlgorithmBase):
    def __init__(self, measurement_name: str, env_configs: List[str | USVEnvironmentDesc], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'pyswarm_PSO_algorithm', env_configs,test_config, number_of_runs, warmups, verbose)
    
    def init_problem(self, env : USVEnvironment, initial_population : List[List[float]], eval_data : EvaluationData):
        lb, ub = self.generate_gene_space(env)
        pos = np.array([np.array(ind) for ind in initial_population])
        # Create a PSO instance
        optimizer = ps.single.GlobalBestPSO(options={'c1': 1.5, 'c2': 1.7, 'w': 0.5},
                                            n_particles=eval_data.population_size, 
                                            dimensions=env.config.all_variable_num,
                                            bounds=(np.array(lb), np.array(ub)),
                                            init_pos=pos)
        aggregate = AggregateAllSwarm(env, minimize=True)
        return optimizer, aggregate
    
    def do_evaluate(self, some_input : Tuple[ps.single.GlobalBestPSO, AggregateAllSwarm], eval_data : EvaluationData):
        optimizer, aggregate = some_input
        start_time = time.time()  # Record the start time
        cost, pos = optimizer.optimize(aggregate.evaluate, iters=np.iinfo(np.int64).max, verbose=self.verbose)
        
        return pos.tolist(), (cost,), np.iinfo(np.int64).max
        
        # Perform optimization with timeout
        best_cost = float('inf')  # Initialize best cost
        best_position = None  # Initialize best position
        iter_count = 0
        while True:
            iter_count += 1
            # Perform a single optimization step
            cost, pos = optimizer.optimize(self.aggregate.evaluate, iters=1, verbose=self.verbose)
            
            # Check if the current cost is the best cost
            if cost < best_cost:
                best_cost = cost
                best_position = pos
            
            # Check for timeout
            elapsed_time = time.time() - start_time
            if cost == 0.0:
                break
            if elapsed_time >= self.runtime:
                break
            
            
        return best_position, best_cost, iter_count
       
    
    def convert_results(self, some_results, eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        best_position, best_cost, iter_count = some_results
        if self.verbose:
            print(f'Best Cost: {best_cost}')
            print(f'Best Position: {best_position}')
            print(f'Iter count: {iter_count}')
        return best_position, best_cost, iter_count
       

    # Attribute generator with different boundaries
    def generate_gene_space(self, env : USVEnvironment):
        xl = [env.config.vessel_descs[0].min_speed]
        xu = [env.config.vessel_descs[0].max_speed]
        for vessel_desc in env.config.vessel_descs[1:]:
            xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel_desc.min_speed]
            xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel_desc.max_speed]
        return xl, xu


    

