from genetic_algorithms.deap_algorithm import DeapAlgorithm
from genetic_algorithms.pygad_algorithm import PyGadAlgorithm
from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from model.usv_environment import USVEnvironment
import random
import time
import itertools


alg = PyMooAlgorithm(measurement_name='test', config_name='seven_vessel_colreg_scenario_one_island', verbose=True, random_init=True)

alg.evaluate(population_size=10, mutate_prob=0.5, crossover_prob=0.5, num_parents_mating=2,
             number_of_generations=None, random_seed=1, mutate_eta=15,    crossover_eta=20)
