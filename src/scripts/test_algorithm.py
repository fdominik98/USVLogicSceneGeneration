from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pymoo_nsga2_algorithm import PyMooNSGA2Algorithm
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pygad_ga_algorithm import PyGadGAAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.pyswarm_pso_algorithm import PySwarmPSOAlgorithm
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.evolutionary_computation.evolutionary_algorithms.scipy_de_algorithm import SciPyDEAlgorithm
from logical_level.models.logical_scenario import LogicalScenario
from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager

de_config = EvaluationData(population_size = 10, mutate_prob = 0.8, crossover_prob=0.5,
                          timeout=10, init_method='uniform', random_seed=22, aggregate_strat='all')

test_config_PSO = EvaluationData(population_size = 10, c_1=1.5, c_2=1.7, w=0.5,
                          timeout=10, init_method='uniform', random_seed=1234, aggregate_strat='all_swarm')

configs = ['two_way_overtaking_BIG', 'overtaking_and_head_on_BIG', 'crossing_and_head_on_BIG', 'two_way_crossing_BIG', 'overtaking_and_crossing_BIG']
configs = ['crossing']

configs = ['two_way_overtaking', 'overtaking_and_head_on', 'crossing_and_head_on', 'two_way_crossing', 'overtaking_and_crossing']
alg = SciPyDEAlgorithm(measurement_name='test_for_progress_report', functional_scenarios=configs, test_config=de_config, number_of_runs=20, warmups=0, verbose=True)

#alg = PySwarmPSOAlgorithm(measurement_name='test_pso', functional_scenarios=['two_way_overtaking'], test_config=test_config_PSO, number_of_runs=1, warmups=0, verbose=True)

#alg = SciPyDEAlgorithm(measurement_name='test_6_vessel_scenarios', functional_scenarios=six_vessel_interactions, test_config=de_config,
#                        number_of_runs=1, warmups=0, verbose=True)

results = alg.run()

#ColregPlotManager(USVEnvironment(alg.functional_scenarios[0]).update(results[0][0].best_solution))
