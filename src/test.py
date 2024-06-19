from genetic_algorithms.deap_algorithm import DeapAlgorithm
from genetic_algorithms.pygad_algorithm import PyGadAlgorithm
from genetic_algorithms.pymoo_algorithm import PyMooAlgorithm
from model.usv_environment import USVEnvironment


# pygad = PyGadAlgorithm(config_name='two_way_overtaking', verbose=1)

# pygad.evaluate(population_size=20, mutate_prob=0.5, crossover_prob=0.5, num_parents_mating=2, number_of_generations=2000, random_seed=1,
#                mutate_eta=None,
#                crossover_eta=None)


deap = PyGadAlgorithm(config_name='two_way_overtaking_and_crossing', verbose=1)

for i in range(200):
    data = deap.evaluate(population_size=30, mutate_prob=0.5, crossover_prob=0.5, num_parents_mating=2, number_of_generations=300, random_seed=i,
                mutate_eta=20,
                crossover_eta=15)
    print(f'{USVEnvironment.euler_distance(data.best_fitness)} - {data.evaluation_time}')