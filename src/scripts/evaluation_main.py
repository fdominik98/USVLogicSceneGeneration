from typing import List

from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.evolutionary_computation.aggregates import ActorAggregate, AggregateAll, AggregateAllSwarm, CategoryAggregate
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.scipy_de_algorithm import SciPyDEAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pyswarm_pso_algorithm import PySwarmPSOAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.evolutionary_algorithm_base import EvolutionaryAlgorithmBase
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pymoo_nsga3_algorithm import PyMooNSGA3Algorithm
from logical_level.mapping.instance_initializer import RandomInstanceInitializer
from logical_level.models.logical_model_manager import LogicalModelManager

# NUMBER_OF_RUNS = {2 : 150, 3 : 6 * 17, 4 : 21 * 5, 5 : 50 * 2, 6 : 99 * 1}
# NUMBER_OF_RUNS = {2 : 150, 3 : 6 * 34, 4 : 21 * 10, 5 : 50 * 4, 6 : 99 * 3}
# NUMBER_OF_RUNS = {2 : 150, 3 : 6 * 50, 4 : 21 * 15, 5 : 50 * 6, 6 : 99 * 4}
NUMBER_OF_RUNS = {2 : 1000, 3 : 1000, 4 : 1000, 5 : 1000, 6 : 1000}
WARMUPS = 2
RANDOM_SEED = 1234
TIMEOUT = 240
INIT_METHOD = RandomInstanceInitializer.name
VERBOSE = False

START_FROM = [0,0,0]

measurement_names= ['test_2_vessel_scenarios', 'test_3_vessel_scenarios', 'test_4_vessel_scenarios',
                    'test_5_vessel_scenarios', 'test_6_vessel_scenarios']
#interactions = [FunctionalModelManager.get_x_vessel_scenarios(3)]
interactions = [LogicalModelManager.get_x_vessel_scenarios(2), LogicalModelManager.get_x_vessel_scenarios(3),
                LogicalModelManager.get_x_vessel_scenarios(4), LogicalModelManager.get_x_vessel_scenarios(5),
                LogicalModelManager.get_x_vessel_scenarios(6)]


ga_config = EvaluationData(population_size=4, num_parents_mating = 4,
                        mutate_eta=20, mutate_prob=0.2, crossover_eta=10,
                        crossover_prob=0.2, timeout=TIMEOUT, init_method=INIT_METHOD,
                        random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name)


nsga2_vessel_config = EvaluationData(population_size=10, mutate_eta=15, mutate_prob=0.8,
                            crossover_eta=20, crossover_prob=1, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=ActorAggregate.name,
                            config_group='SBO')
nsga2_all_config = EvaluationData(population_size=50, mutate_eta=10, mutate_prob=1.0,
                            crossover_eta=20, crossover_prob=0.8, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name)
nsga2_category_config = EvaluationData(population_size=4, mutate_eta=5, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=CategoryAggregate.name)


nsga3_vessel_config = EvaluationData(population_size=6, mutate_eta=15, mutate_prob=1.0,
                            crossover_eta=10, crossover_prob=0.8, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=ActorAggregate.name)
nsga3_all_config = EvaluationData(population_size=20, mutate_eta=1, mutate_prob=0.8,
                            crossover_eta=1, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name)
nsga3_category_config = EvaluationData(population_size=4, mutate_eta=5, mutate_prob=0.8,
                            crossover_eta=15, crossover_prob=1.0, timeout=TIMEOUT,
                            init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=CategoryAggregate.name)


pso_config = EvaluationData(population_size=30, c_1=2.5, c_2=1.0, w=0.4, timeout=TIMEOUT,
                          init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAllSwarm.name)

de_config = EvaluationData(population_size=15, mutate_prob=0.5, crossover_prob=0.5,
                          timeout=TIMEOUT, init_method=INIT_METHOD, random_seed=RANDOM_SEED, aggregate_strat=AggregateAll.name)

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
            interactions_to_run = interaction[interac_group_start:]
        else:
            interactions_to_run = interaction 
        
        number_of_runs_per_interaction = int(NUMBER_OF_RUNS[interactions_to_run[0].size] / len(interactions_to_run))
        one_interaction = [algo(measurement_name=measurement_name, functional_scenarios=interactions_to_run, test_config=config,
                                number_of_runs=number_of_runs_per_interaction, warmups=WARMUPS, verbose=VERBOSE)]
        tests += one_interaction

for test in tests: 
    test.run()
        