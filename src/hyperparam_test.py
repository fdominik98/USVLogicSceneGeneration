from genetic_algorithms.deap_algorithm import DeapAlgorithm
from genetic_algorithms.pygad_algorithm import PyGadAlgorithm
from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from model.usv_environment import USVEnvironment
import random
import time
import itertools

RANDOM_SEED = 1234

population_sizes = [2, 4, 7, 10, 15, 20, 30, 50, 100, 150, 200]
#numbers_of_generations = [50, 100, 200, 400, 1000, 2000]
numbers_of_generations = [None]
#numbers_of_parents = [2, 4, 8, 10]
numbers_of_parents = [2]
mutate_probs = [0.2, 0.5, 0.8, 1]
crossover_probs = [0.2, 0.5, 0.8, 1]
mutate_etas = [1, 5, 10, 15, 20]
crossover_etas = [1, 5, 10, 15, 20]

algos = {
    # 0 : PyMooAlgorithm(measurement_name='parameter_optimization_test', config_name='crossing_and_head_on', verbose=False, random_init=False),    
    # 1 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='crossing_and_head_on', verbose=False, random_init=True),
    # 2 : PyMooAlgorithm(measurement_name='parameter_optimization_test', config_name='two_way_overtaking_and_crossing', verbose=False, random_init=False),
    # 3 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='two_way_overtaking_and_crossing', verbose=False, random_init=True),
    # 4 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='six_vessel_colreg_scenario', verbose=False, random_init=True),
    5 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='seven_vessel_colreg_scenario_one_island', verbose=False, random_init=True),
}

for algo in algos.values():
    all_combinations = itertools.product(population_sizes, numbers_of_generations, numbers_of_parents, mutate_probs, crossover_probs, mutate_etas, crossover_etas)
    combinations_list = list(all_combinations)
    random.seed(time.time())
    random.shuffle(combinations_list)
        
    while len(combinations_list) != 0:
        population_size, number_of_generations, number_of_parents, mutate_prob, crossover_prob, mutate_eta, crossover_eta = combinations_list[0]
            
        try:
            print(f'trying {combinations_list[0]}')
            data = algo.evaluate(population_size=population_size,
                                mutate_prob=mutate_prob, 
                                crossover_prob=crossover_prob, 
                                num_parents_mating=number_of_parents,
                                number_of_generations=number_of_generations, 
                                random_seed=RANDOM_SEED, 
                                mutate_eta=mutate_eta,
                                crossover_eta=crossover_eta)
        except:
            pass
        finally:
            del combinations_list[0]