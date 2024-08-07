
from genetic_algorithms.evaluation_data import EvaluationData
from model.usv_config import *
from aggregates import Aggregate
from genetic_algorithms.genetic_algorithm_base import GeneticAlgorithmBase
from aggregates import VesselAggregate
from model.usv_config import *
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
import matplotlib.pyplot as plt
import matplotlib

from model.usv_environment import USVEnvironment
matplotlib.cm.get_cmap = matplotlib.colormaps.get_cmap
from pymoo.core.population import Population
from model.usv_environment_config import USVEnvironmentConfig
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
        
        if algorithm.callback.best_objective is None:
            return 0.0
        
        f_dist = USVEnvironment.euler_distance(algorithm.callback.best_objective)
        if f_dist == 0.0:
            if self.verbose:
                print("Stopping as a solution with the desired fitness value is found.")
            return 1.0
        
        return 0.0


class BestSolutionCallback(Callback):
    def __init__(self, verbose : bool):
        super().__init__()
        self.verbose = verbose
        self.best_solution = None
        self.best_objective = None
        self.best_dist = None
        self.number_of_generations = 0

    def notify(self, algorithm):
        current_pop = algorithm.pop
        for ind in current_pop:
            f_dist = USVEnvironment.euler_distance(ind.F)
            if self.best_dist == None or (f_dist < self.best_dist):
                self.best_solution = ind.X
                self.best_objective = ind.F
                self.best_dist = f_dist
                if self.verbose:
                    print(f"New best solution found: {ind.X} with objective: {ind.F}")
        self.number_of_generations += 1

class PyMooAlgorithm(GeneticAlgorithmBase):
    
    def __init__(self, measurement_name : str, config_name: str, verbose : bool, random_init : bool = False) -> None:
        super().__init__(measurement_name, 'pymoo_algorithm', config_name, verbose, random_init)
    
    def get_aggregate(self, env) -> Aggregate:
        return VesselAggregate(env, minimize=True)   
    
    
    def init_problem(self, initial_population : list[list[float]], eval_data : EvaluationData):
            # Define the custom multi-objective optimization problem
            class MyProblem(ElementwiseProblem):
                def __init__(self, env_config : USVEnvironmentConfig, aggregate : Aggregate, boundaries):
                    self.aggregate = aggregate
                    self.boundaries = boundaries
                    super().__init__(n_var=env_config.variable_num,  # Number of decision variables
                                    n_obj=aggregate.obj_num,  # Number of objective functions
                                    n_constr=0,  # Number of constraints
                                    xl=[b[0] for b in self.boundaries] * env_config.actor_num, # Lower bounds for variables
                                    xu=[b[1] for b in self.boundaries] * env_config.actor_num)  # Upper bounds for variables

                def _evaluate(self, x, out, *args, **kwargs):
                    out["F"] = self.aggregate.evaluate(x)

            # Instantiate the problem
            problem = MyProblem(self.env_config, self.aggregate, self.boundaries)
            initial_population = Population.new("X", initial_population)
            
            # Define the NSGA-II algorithm
            algorithm = NSGA2(pop_size=eval_data.population_size,
                              crossover=SBX(eta=eval_data.crossover_eta, prob=eval_data.crossover_prob,),
                              mutation=PM(eta=eval_data.mutate_eta, prob=eval_data.mutate_prob), sampling=initial_population,)

            callback = BestSolutionCallback(self.verbose)
            #termination=("n_gen", eval_data.number_of_generations),
            termination = OptimumTermination(time.time(), 300, self.verbose)
            return problem, algorithm, callback, termination

    
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        # Perform the optimization
        problem, algorithm, callback, termination = some_input
        res = minimize(problem,
                  algorithm,                  
                  seed=eval_data.random_seed,
                  save_history=self.verbose,
                  verbose=self.verbose,
                  termination=termination,
                  callback=callback)
        return res, callback
    
    def convert_results(self, some_results, eval_data : EvaluationData) -> tuple[list[float], list[float], int]:
        res, callback = some_results
        if self.verbose:
            # Plot the convergence
            n_evals = []  # corresponding number of function evaluations
            opt = []      # the optima for each evaluation

            for entry in res.history:
                n_evals.append(entry.evaluator.n_eval)
                opt.append(entry.opt[0].F)

            plt.figure(figsize=(7, 5))
            plt.plot(n_evals, opt, marker="o")
            plt.title("Convergence")
            plt.xlabel("Number of Evaluations")
            plt.ylabel("Optimum Value")
            plt.show()

        # X = res.X.tolist()
        # X = sorted(X, key=self.env.evaluate)
        # Extract the decision variables (X) and objective values (F)
        # return X[0], self.aggregate.evaluate(X[0])
        return (list(callback.best_solution), list(callback.best_objective), callback.number_of_generations)



    

