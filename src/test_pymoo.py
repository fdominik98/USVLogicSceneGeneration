from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from visualization.colreg_plot import ColregPlot


alg = PyMooAlgorithm(measurement_name='test', config_name='overtaking_headon_crossing', verbose=True, random_init=True, runtime=120)

data = alg.evaluate(population_size=10, mutate_prob=1.0, crossover_prob=0.2, num_parents_mating=2,
             number_of_generations=None, random_seed=1234, mutate_eta=5,crossover_eta=1)
ColregPlot(alg.env.update(data.best_solution))
