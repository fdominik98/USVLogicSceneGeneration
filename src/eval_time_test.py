from evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
import time

NUMBER_OF_RUNS = 100
RANDOM_SEED = 1234

population_sizes =          [5,     5,      10,     5,      10,     10]
numbers_of_generations =    [None,  None,   None,   None,   None,   None]
numbers_of_parents =        [2,     2,      2,      2,      2,      2]
mutate_probs =              [0.5,   1.0,    0.8,    0.8,    0.5,    1]
crossover_probs =           [0.8,   1.0,    1.0,    0.8,    1.0,    1]
mutate_etas =               [1.0,   1.0,    1.0,    5.0,    1.0,    20]
crossover_etas =            [10.0,  20.0,   15.0,   5.0,    20.0,   15]

combinations_list = list(zip(population_sizes, numbers_of_generations, numbers_of_parents, mutate_probs, crossover_probs, mutate_etas, crossover_etas))

algos = {
    # 1 : PyMooAlgorithm(measurement_name='evaluation_time_test_random', config_name='crossing_and_head_on', verbose=False),
    # 3 : PyMooAlgorithm(measurement_name='evaluation_time_test_random', config_name='two_way_overtaking_and_crossing', verbose=False),
    # 4 : PyMooAlgorithm(measurement_name='evaluation_time_test_random', config_name='six_vessel_colreg_scenario', verbose=False),
    5 : PyMooNSGA2Algorithm(measurement_name='evaluation_time_test_before_safety_distance', config_name='six_vessel_colreg_scenario', verbose=False, runtime=90),
}
for algo_key in algos.keys():    
    population_size, number_of_generations, number_of_parents, mutate_prob, crossover_prob, mutate_eta, crossover_eta = combinations_list[algo_key]
    algo = algos[algo_key]
    print(f'trying {algo.measurement_id} for {algo.config_name} with {combinations_list[algo_key]}')
    for i in range(NUMBER_OF_RUNS):
        print(f'measurement {i}')
      
        data = algo.evaluate(population_size=population_size,
                            mutate_prob=mutate_prob, 
                            crossover_prob=crossover_prob, 
                            num_parents_mating=number_of_parents,
                            number_of_generations=number_of_generations, 
                            random_seed=RANDOM_SEED, 
                            mutate_eta=mutate_eta,
                            crossover_eta=crossover_eta)