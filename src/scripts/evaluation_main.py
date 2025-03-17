from typing import List

from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.constraint_satisfaction.solver_factory import SolverFactory
from logical_level.models.logical_model_manager import LogicalModelManager
from utils.evaluation_config import NUMBER_OF_RUNS, VERBOSE, WARMUPS, nsga2_vessel_sb_o_config, scenic_rs_o_config, scenic_rs_msr_config, nsga2_vessel_sb_msr_config


measurements = [
    # ('test_2_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), nsga2_vessel_sb_o_config),
    # ('test_3_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), nsga2_vessel_sb_o_config),
    # ('test_4_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), nsga2_vessel_sb_o_config),
    # ('test_5_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), nsga2_vessel_sb_o_config),
    # ('test_6_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), nsga2_vessel_sb_o_config),
    
    ('test_2_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), nsga2_vessel_sb_msr_config),
    # ('test_3_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), nsga2_vessel_sb_msr_config),
    # ('test_4_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), nsga2_vessel_sb_msr_config),
    # ('test_5_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), nsga2_vessel_sb_msr_config),
    # ('test_6_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), nsga2_vessel_sb_msr_config),
    
    # ('test_2_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), scenic_rs_o_config),
    # ('test_3_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), scenic_rs_o_config),
    # ('test_4_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), scenic_rs_o_config),
    # ('test_5_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), scenic_rs_o_config),
    # ('test_6_vessel_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), scenic_rs_o_config),
    
    # ('test_2_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), scenic_rs_msr_config),
    # ('test_3_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), scenic_rs_msr_config),
    # ('test_4_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), scenic_rs_msr_config),
    # ('test_5_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), scenic_rs_msr_config),
    # ('test_6_vessel_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), scenic_rs_msr_config), 
    
]


#----------------------------------------------------------

tests : List[SolverBase] = [SolverFactory.factory(measurement_name=measurement_name,
                                                functional_scenarios=interactions_to_run, test_config=config,
                                                number_of_runs=NUMBER_OF_RUNS[interactions_to_run[0].actor_number_by_type],
                                                warmups=WARMUPS, verbose=VERBOSE)
                            for (measurement_name, interactions_to_run, config) in measurements]

for test in tests: 
    test.run()
        