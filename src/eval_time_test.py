from genetic_algorithms.deap_algorithm import DeapAlgorithm
from genetic_algorithms.pygad_algorithm import PyGadAlgorithm
from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
import time

NUMBER_OF_RUNS = 100
RANDOM_SEED = 1234

population_sizes = [5, 5, 10, 5, 10, 10]
numbers_of_generations = [None, None, None, None, None, None]
numbers_of_parents = [2, 2, 2, 2, 2, 2]
mutate_probs = [0.5, 1.0, 0.8, 0.8, 0.5, 0.5]
crossover_probs = [0.8, 1.0, 1.0, 0.8, 1.0, 1.0]
mutate_etas = [1.0, 1.0, 1.0, 5.0, 1.0, 1.0]
crossover_etas = [10.0, 20.0, 15.0, 5.0, 20.0, 20.0]

combinations_list = list(zip(population_sizes, numbers_of_generations, numbers_of_parents, mutate_probs, crossover_probs, mutate_etas, crossover_etas))

algos = {
    # 0 : PyMooAlgorithm(measurement_name='evaluation_time_test', config_name='crossing_and_head_on', verbose=False, random_init=False),    
    # 1 : PyMooAlgorithm(measurement_name='evaluation_time_test_random', config_name='crossing_and_head_on', verbose=False, random_init=True),
    # 2 : PyMooAlgorithm(measurement_name='evaluation_time_test', config_name='two_way_overtaking_and_crossing', verbose=False, random_init=False),
    # 3 : PyMooAlgorithm(measurement_name='evaluation_time_test_random', config_name='two_way_overtaking_and_crossing', verbose=False, random_init=True),
    # 4 : PyMooAlgorithm(measurement_name='evaluation_time_test_random', config_name='six_vessel_colreg_scenario', verbose=False, random_init=True),
    5 : PyMooAlgorithm(measurement_name='evaluation_time_test_random', config_name='seven_vessel_colreg_scenario_one_island', verbose=False, random_init=True),
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