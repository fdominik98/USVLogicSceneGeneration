
from typing import List
from evolutionary_computation.evaluation_data import EvaluationData
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from model.environment.usv_environment import USVEnvironment
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga_algorithm import BestSolutionCallback, NSGAProblem, OptimumTermination, PyMooNSGAAlgorithm
from pymoo.core.population import Population
from model.environment.usv_environment_desc import USVEnvironmentDesc
import time

class PyMooNSGA2Algorithm(PyMooNSGAAlgorithm):
    
    def __init__(self, measurement_name: str, env_configs: List[str | USVEnvironmentDesc], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'pymoo_NSGA2_algorithm', env_configs,test_config, number_of_runs, warmups, verbose)
        
    
    def init_problem(self, env : USVEnvironment, initial_population : List[List[float]], eval_data : EvaluationData):
                        # Instantiate the problem
            problem = NSGAProblem(env, eval_data)
            initial_population = Population.new("X", initial_population)
            
            # Define the NSGA-II algorithm
            algorithm = NSGA2(pop_size=eval_data.population_size,
                              crossover=SBX(eta=eval_data.crossover_eta, prob=eval_data.crossover_prob,),
                              mutation=PM(eta=eval_data.mutate_eta, prob=eval_data.mutate_prob), sampling=initial_population,)

            callback = BestSolutionCallback(time.time(), self.verbose)
            termination = OptimumTermination(time.time(), eval_data.timeout, self.verbose)
            return problem, algorithm, callback, termination

    

