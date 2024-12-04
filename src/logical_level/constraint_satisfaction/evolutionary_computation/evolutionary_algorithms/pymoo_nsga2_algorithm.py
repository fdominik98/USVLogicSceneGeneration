
from typing import List
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from logical_level.models.logical_scenario import LogicalScenario
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pymoo_nsga_algorithm import BestSolutionCallback, NSGAProblem, OptimumTermination, PyMooNSGAAlgorithm
from pymoo.core.population import Population
from functional_level.metamodels.functional_scenario import FunctionalScenario
import time

class PyMooNSGA2Algorithm(PyMooNSGAAlgorithm):
    
    def __init__(self, measurement_name: str, functional_scenarios: List[str | FunctionalScenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'pymoo_NSGA2_algorithm', functional_scenarios,test_config, number_of_runs, warmups, verbose)
        
    
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
                        # Instantiate the problem
            problem = NSGAProblem(logical_scenario, eval_data)
            initial_population = Population.new("X", initial_population)
            
            # Define the NSGA-II algorithm
            algorithm = NSGA2(pop_size=eval_data.population_size,
                              crossover=SBX(eta=eval_data.crossover_eta, prob=eval_data.crossover_prob,),
                              mutation=PM(eta=eval_data.mutate_eta, prob=eval_data.mutate_prob), sampling=initial_population,)

            callback = BestSolutionCallback(time.time(), self.verbose)
            termination = OptimumTermination(time.time(), eval_data.timeout, self.verbose)
            return problem, algorithm, callback, termination

    

