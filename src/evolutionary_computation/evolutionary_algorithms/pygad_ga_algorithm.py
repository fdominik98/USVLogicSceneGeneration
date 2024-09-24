
import time
from typing import List, Tuple
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.usv_config import *
from evolutionary_computation.aggregates import Aggregate
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import GeneticAlgorithmBase
import pygad
from evolutionary_computation.aggregates import AggregateAll
from model.environment.usv_config import *

class PyGadGAAlgorithm(GeneticAlgorithmBase):
    
    def __init__(self, measurement_name : str, config_name: str, verbose : bool, random_init : bool = True, runtime : int = 300) -> None:
        super().__init__(measurement_name, 'pygad_GA_algorithm', config_name, verbose, random_init, runtime)
    
    def get_aggregate(self, env) -> Aggregate:
        return AggregateAll(env)   
    
    
    def init_problem(self, initial_population : List[List[float]], eval_data : EvaluationData) -> None:
        def fitness_func(cls, solution, solution_idx):
            return self.aggregate.evaluate(solution)[0]
        
        start_time = time.time()
        
        def on_generation(ga_instance : pygad.GA):
            if self.verbose:
                print(f"Generation = {ga_instance.generations_completed}")
                print(f"Best solution = {ga_instance.best_solution()}")
            elapsed_time = time.time() - start_time
            solution, solution_fitness, solution_idx = ga_instance.best_solution()
            if solution_fitness == 0.0:
                print(f"Terminating due to fitness reaching 0.0.")
                raise StopIteration
            if elapsed_time > self.runtime:
                print(f"Terminating due to timeout of {self.runtime} seconds.")
                raise StopIteration
            
        # Setting up the GA
        ga_instance : pygad.GA = pygad.GA(
            num_generations=eval_data.number_of_generations,
            num_parents_mating=eval_data.num_parents_mating,
            fitness_func=fitness_func,
            sol_per_pop=eval_data.population_size,
            num_genes=self.env_config.all_variable_num,
            gene_space=self.generate_gene_space(),
            initial_population=initial_population,
            on_generation=on_generation,
            mutation_probability=eval_data.mutate_prob,
            crossover_probability=eval_data.crossover_prob,
            random_seed=eval_data.random_seed,
            #parallel_processing=('thread', 4)
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

    # Attribute generator with different boundaries
    def generate_gene_space(self):
        xl = [self.env.config.vessel_descs[0].min_speed]
        xu = [self.env.config.vessel_descs[0].max_speed]
        for vessel_desc in self.env.config.vessel_descs[1:]:
            xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel_desc.min_speed]
            xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel_desc.max_speed]
        return [{'low': low, 'high': high} for low, high in zip(xl, xu)]


    

