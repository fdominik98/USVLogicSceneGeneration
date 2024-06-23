from genetic_algorithms.deap_algorithm import DeapAlgorithm
from genetic_algorithms.pygad_algorithm import PyGadAlgorithm
from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from model.usv_environment import USVEnvironment
import random
import time
import itertools


# pygad = PyGadAlgorithm(config_name='two_way_overtaking', verbose=1)

# pygad.evaluate(population_size=20, mutate_prob=0.5, crossover_prob=0.5, num_parents_mating=2, number_of_generations=2000, random_seed=1,
#                mutate_eta=None,
#                crossover_eta=None)
population_sizes = [2, 5, 10, 20, 50, 100, 150, 200]
numbers_of_generations = [50, 100, 200, 400, 1000, 2000]
numbers_of_parents = [2, 4, 8, 10]
mutate_probs = [0.2, 0.5, 0.8, 1]
crossover_probs = [0.2, 0.5, 0.8, 1]
mutate_etas = [1, 5, 10, 15, 20]
crossover_etas = [1, 5, 10, 15, 20]

max_number_of_comb = (len(population_sizes) * len(numbers_of_generations) * len(numbers_of_parents) * len(mutate_probs)
                            * len(crossover_probs) * len(mutate_etas) * len(crossover_etas))

algo = PyGadAlgorithm(measurement_name='parameter_optimization', config_name='two_way_overtaking', verbose=False)

all_combinations = itertools.product(population_sizes, numbers_of_generations, numbers_of_parents, mutate_probs, crossover_probs, mutate_etas, crossover_etas)
combinations_list = list(all_combinations)
random.seed(time.time())
random.shuffle(combinations_list)
    
while len(combinations_list) != 0:
    param_config = combinations_list[0]
    population_size, number_of_generations, number_of_parents, mutate_prob, crossover_prob, mutate_eta, crossover_eta = combinations_list[0]
        
    try:
        print(f'trying {param_config}')
        data = algo.evaluate(population_size=population_size,
                             mutate_prob=mutate_prob, 
                             crossover_prob=crossover_prob, 
                             num_parents_mating=number_of_parents,
                             number_of_generations=number_of_generations, 
                             random_seed=1, 
                             mutate_eta=mutate_eta,
                             crossover_eta=crossover_eta)
    except:
        pass
    finally:
        del combinations_list[0]