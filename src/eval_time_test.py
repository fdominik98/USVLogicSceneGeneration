from typing import List
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from evolutionary_computation.evolutionary_algorithms.scipy_de_algorithm import SciPyDEAlgorithm
from evolutionary_computation.evolutionary_algorithms.pyswarm_pso_algorithm import PySwarmPSOAlgorithm
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import GeneticAlgorithmBase
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.functional_models.three_vessel_interactions import three_vessel_interactions
from model.environment.functional_models.four_vessel_interactions import four_vessel_interactions
from model.environment.functional_models.five_vessel_interactions import five_vessel_interactions
from model.environment.functional_models.six_vessel_interactions import six_vessel_interactions
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga3_algorithm import PyMooNSGA3Algorithm

NUMBER_OF_RUNS = 10
WARMUPS = 1
RANDOM_SEED = 1234
TIMEOUT = 60
INIT_METHOD = 'uniform'
VERBOSE = False
measurement_names = ['test_3_vessel_scenarios_lhs', 'test_4_vessel_scenarios_lhs', 'test_5_vessel_scenarios_lhs', 'test_6_vessel_scenarios_lhs']
measurement_names = ['test_3_vessel_scenarios_nsga', 'test_4_vessel_scenarios_nsga', 'test_5_vessel_scenarios_nsga', 'test_6_vessel_scenarios_nsga']
measurement_names = ['test_3_vessel_scenarios', 'test_4_vessel_scenarios', 'test_5_vessel_scenarios', 'test_6_vessel_scenarios']

interactions = [three_vessel_interactions, four_vessel_interactions, five_vessel_interactions, six_vessel_interactions]


ga_config = EvaluationData(population_size=4, num_parents_mating = 4,
                        mutate_eta=20, mutate_prob=0.2, crossover_eta=10,
                        crossover_prob=0.2, timeout=TIMEOUT, init_method=INIT_METHOD,
                        random_seed=RANDOM_SEED, aggregate_strat='all')


nsga2_vessel_config = EvaluationData(population_size=20, mutate_eta=15, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=0.8, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat='vessel')
nsga2_all_config = EvaluationData(population_size=50, mutate_eta=10, mutate_prob=1.0,
                            crossover_eta=20, crossover_prob=0.8, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat='all')
nsga2_category_config = EvaluationData(population_size=4, mutate_eta=5, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat='category')


nsga3_vessel_config = EvaluationData(population_size=6, mutate_eta=10, mutate_prob=1.0,
                            crossover_eta=5, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat='vessel')
nsga3_all_config = EvaluationData(population_size=20, mutate_eta=1, mutate_prob=0.8,
                            crossover_eta=1, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat='all')
nsga3_category_config = EvaluationData(population_size=4, mutate_eta=5, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat='category')


pso_config = EvaluationData(population_size=30, c_1=2.5, c_2=1.0, w=0.4, timeout=TIMEOUT,
                          init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat='all_swarm')

de_config = EvaluationData(population_size=15, mutate_prob=0.5, crossover_prob=0.5,
                          timeout=TIMEOUT, init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat='all')


algos = [PyGadGAAlgorithm, PyMooNSGA2Algorithm, PyMooNSGA2Algorithm, PyMooNSGA2Algorithm, PyMooNSGA3Algorithm, PyMooNSGA3Algorithm, PyMooNSGA3Algorithm, PySwarmPSOAlgorithm, SciPyDEAlgorithm]
configs = [ga_config, nsga2_vessel_config, nsga2_all_config, nsga2_category_config, nsga3_vessel_config, nsga3_all_config, nsga3_category_config, pso_config, de_config]

warmup_tests = [algo(measurement_name=measurement_names[0], env_configs=three_vessel_interactions[:1], test_config=config, number_of_runs=0, warmups=WARMUPS, verbose=VERBOSE) for algo, config in zip(algos, configs)]

tests : List[GeneticAlgorithmBase] = warmup_tests
for measurement_name, interaction in zip(measurement_names, interactions):
    one_interaction = [algo(measurement_name=measurement_name, env_configs=interaction, test_config=config, number_of_runs=NUMBER_OF_RUNS, warmups=0, verbose=VERBOSE) for algo, config in zip(algos, configs)]
    tests += one_interaction

for test in tests: 
    test.run()
        