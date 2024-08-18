from genetic_algorithms.deap_algorithm import DeapAlgorithm
from genetic_algorithms.pygad_algorithm import PyGadAlgorithm
from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from model.usv_environment import USVEnvironment
import random
import time
import itertools
from visualization.colreg_plot import ColregPlot


alg = PyMooAlgorithm(measurement_name='test', config_name='seven_vessel_colreg_scenario', verbose=True, random_init=True, runtime=1000)

data = alg.evaluate(population_size=7, mutate_prob=0.2, crossover_prob=0.8, num_parents_mating=2,
             number_of_generations=None, random_seed=1234, mutate_eta=5,crossover_eta=20)
ColregPlot(alg.env.update(data.best_solution))
