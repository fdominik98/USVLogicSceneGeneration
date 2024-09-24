from evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from evolutionary_computation.evolutionary_algorithms.pyswarm_pso_algorithm import PySwarmPSOAlgorithm
from visualization.colreg_plot_manager import ColregPlotManager


alg = PySwarmPSOAlgorithm(measurement_name='test', config_name='two_way_crossing', verbose=True, random_init=True, runtime=20)

data = alg.evaluate(population_size=10, mutate_prob=0.5, crossover_prob=1, num_parents_mating=2,
             number_of_generations=None, random_seed=22, mutate_eta=15,crossover_eta=20)
ColregPlotManager(alg.env.update(data.best_solution))
