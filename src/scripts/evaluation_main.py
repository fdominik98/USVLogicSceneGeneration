from typing import List

from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.constraint_satisfaction.solver_factory import SolverFactory
from logical_level.models.logical_model_manager import LogicalModelManager
from utils.evaluation_config import NUMBER_OF_RUNS, START_FROM, VERBOSE, WARMUPS, nsga2_vessel_sb_o_config, scenic_rs_o_config, scenic_rs_msr_config, nsga2_vessel_sb_msr_config

# measurement_names= ['test_2_vessel_scenarios', 'test_3_vessel_scenarios', 'test_4_vessel_scenarios',
#                     'test_5_vessel_scenarios', 'test_6_vessel_scenarios']
# interactions = [LogicalModelManager.get_x_vessel_scenarios(2), LogicalModelManager.get_x_vessel_scenarios(3),
#                 LogicalModelManager.get_x_vessel_scenarios(4), LogicalModelManager.get_x_vessel_scenarios(5),
#                 LogicalModelManager.get_x_vessel_scenarios(6)]

measurement_names= ['test_6_vessel_scenarios', ]
interactions = [FunctionalModelManager.get_x_vessel_scenarios(6)]

measurement_names= ['test_3_vessel_scenarios']
interactions = [LogicalModelManager.get_x_vessel_scenarios(3)]
interactions = [FunctionalModelManager.get_x_vessel_scenarios(3)]

measurement_names= ['test_2_vessel_scenarios']
interactions = [LogicalModelManager.get_x_vessel_scenarios(2)]
interactions = [FunctionalModelManager.get_x_vessel_scenarios(2)]

configs = [nsga2_vessel_sb_o_config]
configs = [nsga2_vessel_sb_msr_config]
configs = [scenic_rs_msr_config]
configs = [nsga2_vessel_sb_o_config, scenic_rs_o_config]
configs = [nsga2_vessel_sb_msr_config, scenic_rs_msr_config]

meas_start = START_FROM[0]
algo_start = START_FROM[1]
interaction_group_start = START_FROM[2]

#----------------------------------------------------------

tests : List[SolverBase] = []
for i, (measurement_name, interaction) in enumerate(zip(measurement_names[meas_start:], interactions[meas_start:])):
    if i == 0:
        configs_to_run = configs[algo_start:]
    else:
        configs_to_run = configs
        
    for config in configs_to_run:   
        if i == 0:
            interactions_to_run = interaction[interaction_group_start:]
        else:
            interactions_to_run = interaction 
        
        number_of_runs_per_interaction = int(NUMBER_OF_RUNS[interactions_to_run[0].size] / len(interactions_to_run))
        one_interaction = [SolverFactory.factory(measurement_name=measurement_name,
                                                 functional_scenarios=interactions_to_run, test_config=config,
                                number_of_runs=number_of_runs_per_interaction, warmups=WARMUPS, verbose=VERBOSE)]
        tests += one_interaction

for test in tests: 
    test.run()
        