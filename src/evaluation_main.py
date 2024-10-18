from typing import List

import numpy as np
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from evolutionary_computation.evolutionary_algorithms.scipy_de_algorithm import SciPyDEAlgorithm
from evolutionary_computation.evolutionary_algorithms.pyswarm_pso_algorithm import PySwarmPSOAlgorithm
from evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import EvolutionaryAlgorithmBase
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.evolutionary_algorithms.pymoo_nsga3_algorithm import PyMooNSGA3Algorithm
from model.environment.functional_models import SBO
from model.environment.functional_models import MSR
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST

NUMBER_OF_RUNS = {3 : 6 * 34, 4 : 21 * 10, 5 : 50 * 4, 6 : 99 * 3}
NUMBER_OF_RUNS = {3 : 6 * 17, 4 : 21 * 5, 5 : 50 * 2, 6 : 99 * 1}
WARMUPS = 2
RANDOM_SEED = 1234
TIMEOUT = 600
INIT_METHOD = 'uniform'
VERBOSE = False

START_FROM = [0,0,0]

measurement_names = ['test_3_vessel_SBO', 'test_3_vessel_MSR']
measurement_names = ['test_4_vessel_SBO', 'test_4_vessel_MSR']
measurement_names = ['test_5_vessel_SBO', 'test_5_vessel_MSR']
measurement_names = ['test_6_vessel_MSR', 'test_6_vessel_SBO']

measurement_names= ['test_3_vessel_scenarios_MSR', 'test_3_vessel_scenarios_SBO', 'test_4_vessel_scenarios_MSR', 'test_4_vessel_scenarios_SBO',
                    'test_5_vessel_scenarios_MSR', 'test_5_vessel_scenarios_SBO', 'test_6_vessel_scenarios_MSR', 'test_6_vessel_scenarios_SBO']

measurement_names= ['test_3_vessel_scenarios_MSR_long', 'test_3_vessel_scenarios_SBO_long', 'test_4_vessel_scenarios_MSR_long', 'test_4_vessel_scenarios_SBO_long',
                    'test_5_vessel_scenarios_MSR_long', 'test_5_vessel_scenarios_SBO_long', 'test_6_vessel_scenarios_MSR_long', 'test_6_vessel_scenarios_SBO_long']

interactions = [SBO.three_vessel_interactions, MSR.three_vessel_interactions]
interactions = [SBO.four_vessel_interactions, MSR.four_vessel_interactions]
interactions = [SBO.five_vessel_interactions, MSR.five_vessel_interactions]
interactions = [MSR.six_vessel_interactions, SBO.six_vessel_interactions]

interactions = [SBO.three_vessel_interactions, SBO.four_vessel_interactions, SBO.five_vessel_interactions, SBO.six_vessel_interactions]

interactions = [MSR.three_vessel_interactions, MSR.four_vessel_interactions, MSR.five_vessel_interactions, MSR.six_vessel_interactions]
interactions = [MSR.three_vessel_interactions, SBO.three_vessel_interactions, MSR.four_vessel_interactions, SBO.four_vessel_interactions, 
                MSR.five_vessel_interactions, SBO.five_vessel_interactions, MSR.six_vessel_interactions, SBO.six_vessel_interactions]


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


algos = [SciPyDEAlgorithm]
configs = [de_config]

algos = [PyMooNSGA2Algorithm, PyMooNSGA3Algorithm, PyMooNSGA2Algorithm, PyMooNSGA3Algorithm, PySwarmPSOAlgorithm, SciPyDEAlgorithm]
configs = [nsga2_category_config, nsga3_all_config, nsga2_vessel_config, nsga3_vessel_config, pso_config, de_config]

algos = [PySwarmPSOAlgorithm]
configs = [pso_config]

algos = [PyMooNSGA2Algorithm]
configs = [nsga2_vessel_config]

meas_start = START_FROM[0]
algo_start = START_FROM[1]
interac_group_start = START_FROM[2]

tests : List[EvolutionaryAlgorithmBase] = []
for i, (measurement_name, interaction) in enumerate(zip(measurement_names[meas_start:], interactions[meas_start:])):
    if i == 0:
        algos_to_run = algos[algo_start:]
        configs_to_run = configs[algo_start:]
    else:
        algos_to_run = algos
        configs_to_run = configs
        
    for algo, config in zip(algos_to_run, configs_to_run):   
        if i == 0:
            interactions_to_tun = interaction[interac_group_start:]
        else:
            interactions_to_tun = interaction 
        
        number_of_runs_per_interaction = int(NUMBER_OF_RUNS[interactions_to_tun[0].vessel_num] / len(interactions_to_tun))
        one_interaction = [algo(measurement_name=measurement_name, env_configs=interactions_to_tun, test_config=config,
                                number_of_runs=number_of_runs_per_interaction, warmups=WARMUPS, verbose=VERBOSE)]
        tests += one_interaction

for test in tests: 
    test.run()
        