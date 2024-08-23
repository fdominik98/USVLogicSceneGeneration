from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from visualization.colreg_plot import ColregPlot


alg = PyMooAlgorithm(measurement_name='test', config_name='overtaking_headon_crossing', verbose=True, random_init=True, runtime=240)

data = alg.evaluate(population_size=10, mutate_prob=1, crossover_prob=1, num_parents_mating=2,
             number_of_generations=None, random_seed=3, mutate_eta=20,crossover_eta=15)
ColregPlot(alg.env.update(data.best_solution))
