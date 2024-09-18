from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from visualization.colreg_plot import ColregPlot


alg = PyMooAlgorithm(measurement_name='test', config_name='crossing_big', verbose=True, random_init=True, runtime=20)

data = alg.evaluate(population_size=10, mutate_prob=0.5, crossover_prob=1, num_parents_mating=2,
             number_of_generations=None, random_seed=1112, mutate_eta=15,crossover_eta=20)
ColregPlot(alg.env.update(data.best_solution))
