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
WARMUPS = 2
RANDOM_SEED = 1234
TIMEOUT = 10
RANDOM_INIT = True
INIT_METHOD = 'uniform'

ga_config = EvaluationData(population_size = 4, num_parents_mating = 2,
                        mutate_eta = 15, mutate_prob = 0.2, crossover_eta=10,
                        crossover_prob=1.0, timeout=TIMEOUT, init_method=INIT_METHOD, random_seed=RANDOM_SEED)

nsga2_config = EvaluationData(population_size = 10, mutate_eta = 10, mutate_prob = 0.5,
                            crossover_eta=20, crossover_prob=0.5, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED)

nsga3_config = EvaluationData(population_size = 30, mutate_eta = 15, mutate_prob = 0.8,
                            crossover_eta=15, crossover_prob=1, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED)

pso_config = EvaluationData(population_size = 50, c_1=2.0, c_2=2.0, w=0.4, timeout=TIMEOUT,
                          init_method=INIT_METHOD, random_seed=RANDOM_SEED)

de_config = EvaluationData(population_size = 10, mutate_prob = 0.8, crossover_prob=0.5,
                          timeout=TIMEOUT, init_method=INIT_METHOD, random_seed=RANDOM_SEED)


tests : List[GeneticAlgorithmBase] = [
    PyGadGAAlgorithm(measurement_name='test_3_vessel_scenarios', env_configs=three_vessel_interactions, test_config=ga_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PyMooNSGA2Algorithm(measurement_name='test_3_vessel_scenarios', env_configs=three_vessel_interactions, test_config=nsga2_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PyMooNSGA3Algorithm(measurement_name='test_3_vessel_scenarios', env_configs=three_vessel_interactions, test_config=nsga3_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PySwarmPSOAlgorithm(measurement_name='test_3_vessel_scenarios', env_configs=three_vessel_interactions, test_config=pso_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    SciPyDEAlgorithm(measurement_name='test_3_vessel_scenarios', env_configs=three_vessel_interactions, test_config=de_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    
    
    PyGadGAAlgorithm(measurement_name='test_4_vessel_scenarios', env_configs=four_vessel_interactions, test_config=ga_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PyMooNSGA2Algorithm(measurement_name='test_4_vessel_scenarios', env_configs=four_vessel_interactions, test_config=nsga2_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PyMooNSGA3Algorithm(measurement_name='test_4_vessel_scenarios', env_configs=four_vessel_interactions, test_config=nsga3_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PySwarmPSOAlgorithm(measurement_name='test_4_vessel_scenarios', env_configs=four_vessel_interactions, test_config=pso_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    SciPyDEAlgorithm(measurement_name='test_4_vessel_scenarios', env_configs=four_vessel_interactions, test_config=de_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    
    
    PyGadGAAlgorithm(measurement_name='test_5_vessel_scenarios', env_configs=five_vessel_interactions, test_config=ga_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PyMooNSGA2Algorithm(measurement_name='test_5_vessel_scenarios', env_configs=five_vessel_interactions, test_config=nsga2_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PyMooNSGA3Algorithm(measurement_name='test_5_vessel_scenarios', env_configs=five_vessel_interactions, test_config=nsga3_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PySwarmPSOAlgorithm(measurement_name='test_5_vessel_scenarios', env_configs=five_vessel_interactions, test_config=pso_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    SciPyDEAlgorithm(measurement_name='test_5_vessel_scenarios', env_configs=five_vessel_interactions, test_config=de_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    
    
    PyGadGAAlgorithm(measurement_name='test_6_vessel_scenarios', env_configs=six_vessel_interactions, test_config=ga_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PyMooNSGA2Algorithm(measurement_name='test_6_vessel_scenarios', env_configs=six_vessel_interactions, test_config=nsga2_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PyMooNSGA3Algorithm(measurement_name='test_6_vessel_scenarios', env_configs=six_vessel_interactions, test_config=nsga3_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    PySwarmPSOAlgorithm(measurement_name='test_6_vessel_scenarios', env_configs=six_vessel_interactions, test_config=pso_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    SciPyDEAlgorithm(measurement_name='test_6_vessel_scenarios', env_configs=six_vessel_interactions, test_config=de_config,
                        number_of_runs=NUMBER_OF_RUNS, warmups=WARMUPS, verbose=False),
    
]
for test in tests: 
    test.run()
        