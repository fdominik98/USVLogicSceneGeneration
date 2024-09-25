import random
import time
import itertools
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm

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
    #1 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='crossing_and_head_on', verbose=False, runtime=15),
    #2 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='two_way_overtaking_and_crossing', verbose=False, runtime=15),
    #3 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='five_vessel_colreg_scenario', verbose=False, runtime=20),
    #4 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='six_vessel_colreg_scenario', verbose=False, runtime=20),
    #5 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='seven_vessel_colreg_scenario', verbose=False, runtime=15),
    #6 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='seven_vessel_colreg_scenario2', verbose=False, runtime=25),
    #7 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='overtaking_and_crossing', verbose=False, runtime=10),
    #8 : PyMooAlgorithm(measurement_name='parameter_optimization_test_random', config_name='overtaking_headon_crossing', verbose=False, runtime=10),
    9 : PyGadGAAlgorithm(measurement_name='parameter_optimization_test_random', env_configs='five_vessel_colreg_scenario', verbose=False, runtime=30),
}

all_combinations = itertools.product(population_sizes, numbers_of_generations, numbers_of_parents, mutate_probs, crossover_probs, mutate_etas, crossover_etas)
combinations_list = list(all_combinations)
random.seed(time.time())
random.shuffle(combinations_list)
        
while len(combinations_list) != 0:
    population_size, number_of_generations, number_of_parents, mutate_prob, crossover_prob, mutate_eta, crossover_eta = combinations_list[0]
    for algo in algos.values():
        try:
            print(f'trying {combinations_list[0]} for {algo.env_configs}')
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