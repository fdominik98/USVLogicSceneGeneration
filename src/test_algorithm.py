from evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from evolutionary_computation.evolutionary_algorithms.pyswarm_pso_algorithm import PySwarmPSOAlgorithm
from evolutionary_computation.evaluation_data import EvaluationData
from evolutionary_computation.evolutionary_algorithms.scipy_de_algorithm import SciPyDEAlgorithm
from model.environment.usv_environment import USVEnvironment
from model.environment.functional_models.f3 import three_vessel_interactions
from model.environment.functional_models.MSR.six_vessel_interactions import six_vessel_interactions
from visualization.colreg_scenarios.colreg_plot_manager import ColregPlotManager

de_config = EvaluationData(population_size = 10, mutate_prob = 0.8, crossover_prob=0.5,
                          timeout=10, init_method='uniform', random_seed=22, aggregate_strat='all')

test_config_PSO = EvaluationData(population_size = 10, c_1=1.5, c_2=1.7, w=0.5,
                          timeout=10, init_method='uniform', random_seed=1234, aggregate_strat='all_swarm')

configs = ['two_way_overtaking_BIG', 'overtaking_and_head_on_BIG', 'crossing_and_head_on_BIG', 'two_way_crossing_BIG', 'overtaking_and_crossing_BIG']
configs = ['crossing']
alg = SciPyDEAlgorithm(measurement_name='test_dse_normal', env_configs=configs, test_config=de_config, number_of_runs=20, warmups=0, verbose=True)

#alg = PySwarmPSOAlgorithm(measurement_name='test_pso', env_configs=['two_way_overtaking'], test_config=test_config_PSO, number_of_runs=1, warmups=0, verbose=True)

#alg = SciPyDEAlgorithm(measurement_name='test_6_vessel_scenarios', env_configs=six_vessel_interactions, test_config=de_config,
#                        number_of_runs=1, warmups=0, verbose=True)

results = alg.run()

#ColregPlotManager(USVEnvironment(alg.env_configs[0]).update(results[0][0].best_solution))
