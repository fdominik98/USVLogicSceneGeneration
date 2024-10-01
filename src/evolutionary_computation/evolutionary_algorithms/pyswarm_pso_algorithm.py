import time
from typing import List, Tuple
import numpy as np
from evolutionary_computation.aggregates import Aggregate
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import GeneticAlgorithmBase
import pyswarms as ps
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.environment.usv_environment import USVEnvironment

class ObjectiveMonitor():
    def __init__(self, env: USVEnvironment, eval_data : EvaluationData, start_time, max_time, verbose) -> None:
        self.verbose = verbose
        self.max_time = max_time
        self.start_time = start_time
        self.best_solution : np.ndarray = np.array([])
        self.best_fitness : float = np.inf
        self.iter_count = 0
        self.aggregate = Aggregate.factory(env, eval_data.aggregate_strat, minimize=True)
        
    def objective(self, x):
        self.iter_count+=1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.max_time:
            if self.verbose:
                print('Stopping due to timeout.')
            raise StopIteration()
        F = self.aggregate.evaluate(x)
        for i, f in enumerate(F):
            if f < self.best_fitness:
                self.best_fitness = f
                self.best_solution = x[i]
        if self.best_fitness <= 0.0:
            if self.verbose:
                print('Optimal fitness reached.')
            raise StopIteration()
        return F
    
    def print(self):
        if self.verbose:
            print(f'Best Position: {self.best_solution}')
            print(f'Best Cost: {self.best_fitness}')
            print(f'Iter count: {self.iter_count}')
    
class PySwarmPSOAlgorithm(GeneticAlgorithmBase):
    
        
    
    def __init__(self, measurement_name: str, env_configs: List[str | USVEnvironmentDesc], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'pyswarm_PSO_algorithm', env_configs,test_config, number_of_runs, warmups, verbose)
    
    def init_problem(self, env : USVEnvironment, initial_population : List[List[float]], eval_data : EvaluationData):
        pos = np.array([np.array(ind) for ind in initial_population])
        # Create a PSO instance
        optimizer = ps.single.GlobalBestPSO(options={'c1': eval_data.c_1, 'c2': eval_data.c_2, 'w': eval_data.w},
                                            n_particles=eval_data.population_size, 
                                            dimensions=env.config.all_variable_num,
                                            bounds=(np.array(env.xl), np.array(env.xu)),
                                            init_pos=pos)
        monitor = ObjectiveMonitor(env, eval_data, time.time(), eval_data.timeout, self.verbose)
        
        return optimizer, monitor
    
    def do_evaluate(self, some_input : Tuple[ps.single.GlobalBestPSO, ObjectiveMonitor], eval_data : EvaluationData):
        optimizer, monitor = some_input
        try:
            optimizer.optimize(monitor.objective, iters=np.iinfo(np.int64).max, verbose=self.verbose)
        except StopIteration:
            pass
        finally:
            return monitor
       
    
    def convert_results(self, some_results : ObjectiveMonitor, eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        some_results.print()
        return some_results.best_solution.tolist(), [some_results.best_fitness,], some_results.iter_count
       

