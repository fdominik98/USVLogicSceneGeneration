import time
from typing import List, Tuple
import numpy as np
from evolutionary_computation.aggregates import Aggregate
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import GeneticAlgorithmBase
from scipy.optimize import differential_evolution, OptimizeResult
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_config import EPSILON

class ObjectiveMonitorCallback:
    def __init__(self, aggregate : Aggregate, max_time_sec, verbose : bool):
        self.start_time = time.time()
        self.max_time_sec = max_time_sec
        self.current_best_objective = np.inf
        self.aggregate = aggregate
        self.verbose = verbose

    def __call__(self, xk, convergence):
        current_time = time.time()
        
        if current_time - self.start_time > self.max_time_sec:
            if self.verbose:
                print("Termination stopped due to timeout")
            return True  # Stop optimization
        
        if self.current_best_objective < EPSILON:
            if self.verbose:
                print("Optimal solution reached")
            return True  # Stop optimization
        return False
    
    def objective(self, solution):
        objective = self.aggregate.evaluate(solution)[0]
        if self.current_best_objective > objective:
            self.current_best_objective = objective
        return objective


class SciPyDEAlgorithm(GeneticAlgorithmBase):
    def __init__(self, measurement_name: str, env_configs: List[str | USVEnvironmentDesc], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'scipy_DE_algorithm', env_configs,test_config, number_of_runs, warmups, verbose)
        self.current_best_objective = np.inf
    
    def init_problem(self, env: USVEnvironment, initial_population : List[List[float]], eval_data : EvaluationData):
        aggregate = Aggregate.factory(env, eval_data.aggregate_strat, minimize=True)
        objective_monitor = ObjectiveMonitorCallback(aggregate, eval_data.timeout, self.verbose)
        return list(zip(env.xl, env.xu)), objective_monitor, initial_population
    
    def do_evaluate(self, some_input : Tuple[List[Tuple[int, int]], ObjectiveMonitorCallback, List[List[float]]], eval_data : EvaluationData):
       bounds, objective_monitor, initial_pop = some_input
       return differential_evolution(objective_monitor.objective, 
                                    bounds,
                                    popsize=eval_data.population_size,
                                    maxiter=np.iinfo(np.int64).max,
                                    tol=-np.inf,                # Relative tolerance for convergence
                                    atol=-np.inf,
                                    mutation=eval_data.mutate_prob,       # Mutation constant
                                    recombination=eval_data.crossover_prob,       # Recombination constant (crossover)
                                    callback=objective_monitor,       # Custom callback to handle time termination
                                    disp=self.verbose,
                                    init=initial_pop)
    
    def convert_results(self, some_results : OptimizeResult, eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        if self.verbose:
            print(some_results)
        iter_num = some_results['nit']
        X : np.ndarray = some_results['x']
        F : np.ndarray = np.array([some_results['fun']])
        return X.tolist(), F.tolist(), iter_num



    

