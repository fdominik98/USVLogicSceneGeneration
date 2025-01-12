import time
from typing import List, Tuple
import numpy as np
from logical_level.constraint_satisfaction.evolutionary_computation.aggregates import Aggregate
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import EvolutionaryAlgorithmBase
from scipy.optimize import differential_evolution, OptimizeResult
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.models.logical_scenario import LogicalScenario
from utils.asv_utils import EPSILON

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
        
        if self.current_best_objective == 0.0:
            if self.verbose:
                print("Optimal solution reached")
            return True  # Stop optimization
        return False
    
    def objective(self, solution):
        objective = self.aggregate.evaluate(solution)[0]
        if self.current_best_objective > objective:
            self.current_best_objective = objective
        return objective


class SciPyDEAlgorithm(EvolutionaryAlgorithmBase):
    def __init__(self, measurement_name: str, functional_scenarios: List[str | FunctionalScenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'scipy_DE_algorithm', functional_scenarios,test_config, number_of_runs, warmups, verbose)
        self.current_best_objective = np.inf
    
    def init_problem(self, logical_scenario : LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
        aggregate = Aggregate.factory(logical_scenario, eval_data.aggregate_strat, minimize=True)
        objective_monitor = ObjectiveMonitorCallback(aggregate, eval_data.timeout, self.verbose)
        return list(zip(logical_scenario.xl, logical_scenario.xu)), objective_monitor, initial_population
    
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



    

