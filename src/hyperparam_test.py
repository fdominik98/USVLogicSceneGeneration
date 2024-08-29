from genetic_algorithms.deap_algorithm import DeapAlgorithm
from genetic_algorithms.pygad_algorithm import PyGadAlgorithm
from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from model.usv_environment import USVEnvironment
import random
import time
import itertools

RANDOM_SEED = 4321

population_sizes = [2, 4, 7, 10, 15, 20, 30, 50, 100]
#numbers_of_generations = [50, 100, 200, 400, 1000, 2000]
numbers_of_generations = [None]
#numbers_of_parents = [2, 4, 8, 10]
numbers_of_parents = [2]
mutate_probs = [0.2, 0.5, 0.8, 1]
crossover_probs = [0.2, 0.5, 0.8, 1]
mutate_etas = [1, 5, 10, 15, 20]
crossover_etas = [1, 5, 10, 15, 20]

algos = {
    #1 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='crossing_and_head_on', verbose=False, random_init=True, runtime=15),
    #2 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='two_way_overtaking_and_crossing', verbose=False, random_init=True, runtime=15),
    #3 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='five_vessel_colreg_scenario', verbose=False, random_init=True, runtime=20),
    #4 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='six_vessel_colreg_scenario', verbose=False, random_init=True, runtime=20),
    #5 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='seven_vessel_colreg_scenario', verbose=False, random_init=True, runtime=15),
    #6 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='seven_vessel_colreg_scenario2', verbose=False, random_init=True, runtime=25),
    7 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='crossing_big', verbose=False, random_init=True, runtime=10),
}

all_combinations = itertools.product(population_sizes, numbers_of_generations, numbers_of_parents, mutate_probs, crossover_probs, mutate_etas, crossover_etas)
combinations_list = list(all_combinations)
random.seed(time.time())
random.shuffle(combinations_list)
        
while len(combinations_list) != 0:
    population_size, number_of_generations, number_of_parents, mutate_prob, crossover_prob, mutate_eta, crossover_eta = combinations_list[0]
    for algo in algos.values():
        try:
            print(f'trying {combinations_list[0]} for {algo.config_name}')
            data = algo.evaluate(population_size=population_size,
                                mutate_prob=mutate_prob, 
                                crossover_prob=crossover_prob, 
                                num_parents_mating=number_of_parents,
                                number_of_generations=number_of_generations, 
                                random_seed=RANDOM_SEED, 
                                mutate_eta=mutate_eta,
                                crossover_eta=crossover_eta)
            print(data)
        except:
            pass
        
    del combinations_list[0]