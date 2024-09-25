
from typing import Any, List, Tuple
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.aggregates import Aggregate
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import GeneticAlgorithmBase
from evolutionary_computation.aggregates import VesselAggregate
from model.environment.usv_config import MAX_HEADING, MIN_COORD, MAX_COORD, MIN_HEADING
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.result import Result
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
import matplotlib.pyplot as plt
import matplotlib

from model.environment.usv_environment import USVEnvironment
matplotlib.cm.get_cmap = matplotlib.colormaps.get_cmap
from pymoo.core.population import Population
from model.environment.usv_environment_desc import USVEnvironmentDesc
from pymoo.core.callback import Callback
from pymoo.core.termination import Termination
import time

class OptimumTermination(Termination):
    def __init__(self, start_time, max_time, verbose):
        super().__init__()
        self.verbose = verbose
        self.max_time = max_time
        self.start_time = start_time

    def _update(self, algorithm):
        # Check for timeout
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.max_time:
            if self.verbose:
                print("Stopping due to timeout.")
            return 1.0
        
        if len(algorithm.callback.best_objective) == 0:
            return 0.0
        
        f_dist = USVEnvironment.euler_distance(algorithm.callback.best_objective)
        if f_dist == 0.0:
            if self.verbose:
                print("Stopping as a solution with the desired fitness value is found.")
            return 1.0
        
        return 0.0


class BestSolutionCallback(Callback):
    def __init__(self, start_time, verbose : bool):
        super().__init__()
        self.verbose = verbose
        self.best_solution : List[float] = []
        self.best_objective : List[float] = []
        self.best_dist = None
        self.number_of_generations = 0
        self.start_time = start_time

    def notify(self, algorithm):
        current_pop = algorithm.pop
        for ind in current_pop:
            f_dist = USVEnvironment.euler_distance(ind.F)
            if self.best_dist == None or (f_dist < self.best_dist):
                self.best_solution = ind.X
                self.best_objective = ind.F
                self.best_dist = f_dist
                if self.verbose:
                    print(f"{int(time.time() - self.start_time)} - New best solution found: {ind.X} with objective: {ind.F}")
        self.number_of_generations += 1

class PyMooNSGA2Algorithm(GeneticAlgorithmBase):
    
    def __init__(self, measurement_name: str, env_configs: List[str | USVEnvironmentDesc], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'pymoo_NSGA2_algorithm', env_configs,test_config, number_of_runs, warmups, verbose)
        
    
    def init_problem(self, env : USVEnvironment, initial_population : List[List[float]], eval_data : EvaluationData):
            # Define the custom multi-objective optimization problem
            class MyProblem(ElementwiseProblem):
                def __init__(self, aggregate : Aggregate):
                    self.aggregate = aggregate
                    xl = [env.config.vessel_descs[0].min_speed]
                    xu = [env.config.vessel_descs[0].max_speed]
                    for vessel_desc in env.config.vessel_descs[1:]:
                        xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel_desc.min_speed]
                        xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel_desc.max_speed]
                    super().__init__(n_var=env.config.all_variable_num,  # Number of decision variables
                                    n_obj=aggregate.obj_num,  # Number of objective functions
                                    n_constr=0,  # Number of constraints
                                    xl=xl, # Lower bounds for variables
                                    xu=xu)  # Upper bounds for variables

                def _evaluate(self, x, out, *args, **kwargs):
                    out["F"] = self.aggregate.evaluate(x)

            # Instantiate the problem
            problem = MyProblem(VesselAggregate(env, minimize=True))
            initial_population = Population.new("X", initial_population)
            
            # Define the NSGA-II algorithm
            algorithm = NSGA2(pop_size=eval_data.population_size,
                              crossover=SBX(eta=eval_data.crossover_eta, prob=eval_data.crossover_prob,),
                              mutation=PM(eta=eval_data.mutate_eta, prob=eval_data.mutate_prob), sampling=initial_population,)

            callback = BestSolutionCallback(time.time(), self.verbose)
            #termination=("n_gen", np.iinfo(np.int64).max),
            termination = OptimumTermination(time.time(), eval_data.timeout, self.verbose)
            return problem, algorithm, callback, termination

    
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        # Perform the optimization
        problem, algorithm, callback, termination = some_input
        res : Result = minimize(problem,
                  algorithm,                  
                  save_history=self.verbose,
                  verbose=self.verbose,
                  termination=termination,
                  callback=callback)
        return res, callback
    
    def convert_results(self, some_results : Tuple[Result, BestSolutionCallback], eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        res, callback = some_results
        if self.verbose:
            # Plot the convergence
            n_evals = []  # corresponding number of function evaluations
            opt = []      # the optima for each evaluation

            for entry in res.history:
                n_evals.append(entry.evaluator.n_eval)
                opt.append(entry.opt[0].F)

            fig, ax = plt.subplots(figsize=(7, 5))
            ax.plot(n_evals, opt, marker="o")
            ax.set_title("Convergence")
            ax.set_xlabel("Number of Evaluations")
            ax.set_ylabel("Optimum Value")
            fig.show()

        # X = res.X.tolist()
        # X = sorted(X, key=self.env.evaluate)
        # Extract the decision variables (X) and objective values (F)
        # return X[0], self.aggregate.evaluate(X[0])
        return (list(callback.best_solution), list(callback.best_objective), callback.number_of_generations)



    

