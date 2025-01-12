
from typing import List
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from logical_level.models.logical_scenario import LogicalScenario
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pymoo_nsga_algorithm import BestSolutionCallback, NSGAProblem, OptimumTermination, PyMooNSGAAlgorithm
from pymoo.core.population import Population
from functional_level.metamodels.functional_scenario import FunctionalScenario
import time

class PyMooNSGA3Algorithm(PyMooNSGAAlgorithm):
    
    def __init__(self, measurement_name: str, functional_scenarios: List[str | FunctionalScenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'pymoo_NSGA3_algorithm', functional_scenarios,test_config, number_of_runs, warmups, verbose)
        
    
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
            # Instantiate the problem
            problem = NSGAProblem(logical_scenario, eval_data)
            initial_population = Population.new("X", initial_population)
            
            if problem.aggregate.object_num > eval_data.population_size:
                eval_data.population_size = problem.aggregate.object_num
            
            ref_dirs = get_reference_directions("das-dennis", problem.aggregate.object_num, n_partitions=1)
            # Define the NSGA-III algorithm
            algorithm = NSGA3(ref_dirs, pop_size=eval_data.population_size,
                              crossover=SBX(eta=eval_data.crossover_eta, prob=eval_data.crossover_prob,),
                              mutation=PM(eta=eval_data.mutate_eta, prob=eval_data.mutate_prob), sampling=initial_population,)

            callback = BestSolutionCallback(time.time(), self.verbose)
            termination = OptimumTermination(time.time(), eval_data.timeout, self.verbose)
            return problem, algorithm, callback, termination

    

