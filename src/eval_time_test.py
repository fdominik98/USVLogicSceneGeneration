from evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.functional_models.three_vessel_interactions import three_vessel_interactions

NUMBER_OF_RUNS = 10
WARMUPS = 0
RANDOM_SEED = 1234
TIMEOUT = 10
RANDOM_INIT = True


test_config1 = EvaluationData(population_size = 10, num_parents_mating = 2,
                        mutate_eta = 20, mutate_prob = 1, crossover_eta=15,
                        crossover_prob=1, timeout=TIMEOUT, random_init=RANDOM_INIT, random_seed=RANDOM_SEED)

tests = [
    PyMooNSGA2Algorithm(measurement_name='test3', env_configs=three_vessel_interactions, test_config=test_config1,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False)
]
for test in tests: 
    test.run()
        