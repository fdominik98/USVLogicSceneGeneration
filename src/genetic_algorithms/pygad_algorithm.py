
from genetic_algorithms.evaluation_data import EvaluationData
from model.usv_config import *
from aggregates import Aggregate
from genetic_algorithms.genetic_algorithm_base import GeneticAlgorithmBase
import pygad
from aggregates import AggregateAll, EulerDistance
from visualization.colreg_plot import ColregPlot
from model.usv_config import *

class PyGadAlgorithm(GeneticAlgorithmBase):
    
    def __init__(self, measurement_name : str, config_name: str, verbose : bool, random_init : bool = False) -> None:
        super().__init__(measurement_name, 'pygad_algorithm', config_name, verbose, random_init)
    
    def get_aggregate(self, env) -> Aggregate:
        return AggregateAll(env)   
    
    
    def init_problem(self, initial_population : list[list[float]], eval_data : EvaluationData) -> None:
            def fitness_func(cls, solution, solution_idx):
                return self.aggregate.evaluate(solution)[0]
            
            def on_generation(ga_instance):
                print(f"Generation = {ga_instance.generations_completed}")
                print(f"Fitness of the best solution = {ga_instance.best_solution()[1]}")
                
            on_generation_func = on_generation if self.verbose else None
            
            # Setting up the GA
            ga_instance = pygad.GA(
                num_generations=eval_data.number_of_generations,
                num_parents_mating=eval_data.num_parents_mating,
                fitness_func=fitness_func,
                sol_per_pop=eval_data.population_size,
                num_genes=self.env_config.all_variable_num,
                gene_space=self.generate_gene_space(self.env_config.actor_num),
                initial_population=initial_population,
                on_generation=on_generation_func,
                mutation_probability=eval_data.mutate_prob,
                crossover_probability=eval_data.crossover_prob,
                random_seed=eval_data.random_seed,
                #parallel_processing=('thread', 4)
            )
            return ga_instance
    
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        # ga_instance
        some_input.run()
        return some_input
    
    def convert_results(self, some_results, eval_data : EvaluationData) -> tuple[list[float], list[float]]:
        ga_instance = some_results
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
        return list(solution.flatten()), [abs(solution_fitness)]

    # Attribute generator with different boundaries
    def generate_gene_space(self, actors):
        return [{'low': low, 'high': high} for low, high in self.boundaries] * actors


    

