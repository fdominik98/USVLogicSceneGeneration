
from genetic_algorithms.evaluation_data import EvaluationData
from model.usv_config import *
from aggregates import Aggregate
from genetic_algorithms.genetic_algorithm_base import GeneticAlgorithmBase
from aggregates import NoAggregate, AggregateAll, EulerDistance
from model.usv_config import *
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
import matplotlib.pyplot as plt
import matplotlib
matplotlib.cm.get_cmap = matplotlib.colormaps.get_cmap
from pymoo.core.population import Population

from model.usv_environment_config import USVEnvironmentConfig

class PyMooAlgorithm(GeneticAlgorithmBase):
    
    def __init__(self, measurement_name : str, config_name: str, verbose : bool) -> None:
        super().__init__(measurement_name, 'pymoo_algorithm', config_name, verbose)
    
    def get_aggregate(self, env) -> Aggregate:
        return NoAggregate(env, minimize=True)   
    
    
    def init_problem(self, initial_population : list[list[float]], eval_data : EvaluationData) -> None:
            # Define the custom multi-objective optimization problem
            class MyProblem(ElementwiseProblem):
                def __init__(self, env_config : USVEnvironmentConfig, aggregate : Aggregate, ):
                    self.aggregate = aggregate
                    super().__init__(n_var=env_config.variable_num,  # Number of decision variables
                                    n_obj=aggregate.obj_num,  # Number of objective functions
                                    n_constr=0,  # Number of constraints
                                    xl=[b[0] for b in boundaries]* env_config.actor_num, # Lower bounds for variables
                                    xu=[b[1] for b in boundaries] * env_config.actor_num)  # Upper bounds for variables

                def _evaluate(self, x, out, *args, **kwargs):
                    out["F"] = self.aggregate.evaluate(x)

            # Instantiate the problem
            problem = MyProblem(self.env_config, self.aggregate)

            initial_population_array = self.env.get_population(eval_data.population_size)
            initial_population = Population.new("X", initial_population_array)
            
            # Define the NSGA-II algorithm
            algorithm = NSGA2(pop_size=eval_data.population_size,
                              crossover=SBX(eta=eval_data.crossover_eta, prob=eval_data.crossover_prob,),
                              mutation=PM(eta=eval_data.mutate_eta, prob=eval_data.mutate_prob), sampling=initial_population,)

            return problem, algorithm

    
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        # Perform the optimization
        problem, algorithm = some_input
        return minimize(problem,
                  algorithm,                  
                  seed=eval_data.random_seed,
                  save_history=self.verbose,
                  verbose=self.verbose,
                  termination=("n_gen", eval_data.number_of_generations))
    
    def convert_results(self, some_results, eval_data : EvaluationData) -> tuple[list[float], list[float]]:
        if self.verbose:
            # Plot the convergence
            n_evals = []  # corresponding number of function evaluations
            opt = []      # the optima for each evaluation

            for entry in some_results.history:
                n_evals.append(entry.evaluator.n_eval)
                opt.append(entry.opt[0].F)

            plt.figure(figsize=(7, 5))
            plt.plot(n_evals, opt, marker="o")
            plt.title("Convergence")
            plt.xlabel("Number of Evaluations")
            plt.ylabel("Optimum Value")
            plt.show()

        X = some_results.X.tolist()
        X = sorted(X, key=self.env.evaluate)
        # Extract the decision variables (X) and objective values (F)
        return X[0], self.aggregate.evaluate(X[0])



    

