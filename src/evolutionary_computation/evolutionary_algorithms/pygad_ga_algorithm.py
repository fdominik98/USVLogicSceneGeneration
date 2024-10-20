
import time
from typing import List, Tuple
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import EvolutionaryAlgorithmBase
import pygad
from evolutionary_computation.aggregates import Aggregate
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_config import EPSILON

class PyGadGAAlgorithm(EvolutionaryAlgorithmBase):
    def __init__(self, measurement_name: str, env_configs: List[str | USVEnvironmentDesc], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'pygad_GA_algorithm', env_configs,test_config, number_of_runs, warmups, verbose)
    
    def init_problem(self,  env: USVEnvironment, initial_population : List[List[float]], eval_data : EvaluationData) -> None:
        def fitness_func(cls, solution, solution_idx):
            return Aggregate.factory(env, eval_data.aggregate_strat, minimize=False).evaluate(solution)[0]
        
        start_time = time.time()
        
        def on_generation(ga_instance : pygad.GA):
            if self.verbose:
                print(f"Generation = {ga_instance.generations_completed}")
                print(f"Best solution = {ga_instance.best_solution()}")
            elapsed_time = time.time() - start_time
            solution, solution_fitness, solution_idx = ga_instance.best_solution()
            if abs(solution_fitness) == 0.0:
                if self.verbose:
                    print(f"Terminating due to fitness reaching 0.0.")
                raise StopIteration
            if elapsed_time > eval_data.timeout:
                if self.verbose:
                    print(f"Terminating due to timeout of {eval_data.timeout} seconds.")
                raise StopIteration
            
        # Setting up the GA
        ga_instance : pygad.GA = pygad.GA(
            num_generations=np.iinfo(np.int64).max,
            num_parents_mating=eval_data.num_parents_mating,
            fitness_func=fitness_func,
            sol_per_pop=eval_data.population_size,
            num_genes=env.config.all_variable_num,
            gene_space=[{'low': low, 'high': high} for low, high in zip(env.xl, env.xu)],
            initial_population=initial_population,
            on_generation=on_generation,
            mutation_probability=eval_data.mutate_prob,
            crossover_probability=eval_data.crossover_prob,
            parent_selection_type='tournament',
            K_tournament=2           
        )
        return ga_instance
    
    def do_evaluate(self, some_input : pygad.GA, eval_data : EvaluationData):
        try:
            # Run the GA
            some_input.run()
        except StopIteration:
            pass
        finally:
            return some_input
    
    def convert_results(self, some_results, eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        ga_instance : pygad.GA= some_results
        # After the GA run, print the best solution found
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        # if self.verbose:
        #     # Get the best solutions
        #     num_best_solutions = 1
        #     population_fitness = ga_instance.last_generation_fitness
        #     sorted_indices = np.argsort(population_fitness)[::-1]  # Sort in descending order of fitness
        #     best_solutions = [ga_instance.population[idx] for idx in sorted_indices[:num_best_solutions]]
        #     for sol in best_solutions:
        #         ColregPlot(self.env.update(sol))
        return list(solution.flatten()), [abs(solution_fitness)], ga_instance.generations_completed



    

