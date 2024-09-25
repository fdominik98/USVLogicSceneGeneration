import random
import time
import itertools
from typing import Any, List, Tuple
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import GeneticAlgorithmBase

NUMBER_OF_RUNS = 1
WARMUPS = 0
RANDOM_SEED = 1234
TIMEOUT = 30
RANDOM_INIT = True

population_sizes = [2, 4, 7, 10, 15, 20, 30, 50, 100]
nums_parents_mating = [2, 4, 8, 10]
mutate_probs = [0.2, 0.5, 0.8, 1]
crossover_probs = [0.2, 0.5, 0.8, 1]
mutate_etas = [1, 5, 10, 15, 20]
crossover_etas = [1, 5, 10, 15, 20]
c1_s = [1.0, 1.5, 2.0, 2.5]
c2_s = [1.0, 1.5, 2.0, 2.5]
w_s = [0.4, 0.6, 0.9]

combinations_GA = list(itertools.product(population_sizes, nums_parents_mating, mutate_probs, crossover_probs, mutate_etas, crossover_etas))
combinations_NSGA2 = list(itertools.product(population_sizes, mutate_probs, crossover_probs, mutate_etas, crossover_etas))
combinations_PSO = list(itertools.product(population_sizes, c1_s, c2_s, w_s))


def create_GA_config() -> EvaluationData:
    if len(combinations_GA) == 0:
        return None
    population_size, num_parents_mating, mutate_prob, crossover_prob, mutate_eta, crossover_eta = combinations_GA[0]
    while num_parents_mating > population_size:
        del combinations_GA[0]
        if len(combinations_GA) == 0:
            return None
        population_size, num_parents_mating, mutate_prob, crossover_prob, mutate_eta, crossover_eta = combinations_GA[0]
        
    return EvaluationData(population_size = population_size, num_parents_mating = num_parents_mating,
            mutate_eta = mutate_eta, mutate_prob = mutate_prob, crossover_eta=crossover_eta,
            crossover_prob=crossover_prob, timeout=TIMEOUT, random_init=RANDOM_INIT, random_seed=RANDOM_SEED)
    
def create_NSGA2_config() -> EvaluationData:
    if len(combinations_NSGA2) == 0:
        return None
    population_size, mutate_prob, crossover_prob, mutate_eta, crossover_eta = combinations_NSGA2[0]
    return EvaluationData(population_size = population_size, mutate_eta = mutate_eta, mutate_prob = mutate_prob,
                          crossover_eta=crossover_eta, crossover_prob=crossover_prob, timeout=TIMEOUT,
                          random_init=RANDOM_INIT, random_seed=RANDOM_SEED)
    
def create_PSO_config() -> EvaluationData:
    if len(combinations_PSO) == 0:
        return None
    population_size, c_1, c_2, w = combinations_PSO[0]
    return EvaluationData(population_size = population_size, c_1=c_1, c_2=c_2, w=w, timeout=TIMEOUT,
                          random_init=RANDOM_INIT, random_seed=RANDOM_SEED)

random.seed(time.time())
random.shuffle(combinations_GA)
random.shuffle(combinations_NSGA2)
random.shuffle(combinations_PSO)




tests : List[Tuple[Any, GeneticAlgorithmBase]]= [
    (create_GA_config, PyGadGAAlgorithm(measurement_name='parameter_optimization',
                                        env_configs=['five_vessel_colreg_scenario'],
                                        test_config=create_GA_config(), number_of_runs=NUMBER_OF_RUNS,
                                        warmups = WARMUPS, verbose=False)),
]


     
while True:
    runs = 0
    for config_fun, test in tests:
        config = config_fun()
        if config is not None:
            test.test_config = config
            test.run()
            runs += 1
    if runs == 0:
        break
    if len(combinations_GA) > 0:   
        del combinations_GA[0]
    if len(combinations_NSGA2) > 0:
        del combinations_NSGA2[0]
    if len(combinations_PSO) > 0:
        del combinations_PSO[0]
