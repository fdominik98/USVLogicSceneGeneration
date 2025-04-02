from multiprocessing import Process
from typing import List, Tuple

from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.constraint_satisfaction.solver_factory import SolverFactory
from logical_level.models.logical_model_manager import LogicalModelManager
from utils.evaluation_config import NUMBER_OF_RUNS, VERBOSE, WARMUPS, nsga2_vessel_sb_o_config, scenic_rs_o_config, scenic_rs_msr_config, nsga2_vessel_sb_msr_config
from utils.scenario import Scenario

class SceneGenerationProcess(Process):
    def __init__(self, solver : SolverBase) -> None:
        super().__init__(target=solver.run, name=solver.measurement_name, daemon=True)

base_name = 'mini_usv_test'

measurements : List[Tuple[str, List[Scenario], EvaluationData]] = [
    # SB-O
    # (f'{base_name}_2_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), nsga2_vessel_sb_o_config),
    # (f'{base_name}_2_vessel_1_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 1), nsga2_vessel_sb_o_config),
    (f'{base_name}_3_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), nsga2_vessel_sb_o_config),
    # (f'{base_name}_3_vessel_1_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 1), nsga2_vessel_sb_o_config),
    # (f'{base_name}_4_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), nsga2_vessel_sb_o_config),
    # (f'{base_name}_5_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), nsga2_vessel_sb_o_config),
    # (f'{base_name}_6_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), nsga2_vessel_sb_o_config),
    
    # SB-MSR
    # (f'{base_name}_2_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), nsga2_vessel_sb_msr_config),
    # (f'{base_name}_2_vessel_1_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 1), nsga2_vessel_sb_msr_config),
    (f'{base_name}_3_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), nsga2_vessel_sb_msr_config),
    # (f'{base_name}_3_vessel_1_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 1), nsga2_vessel_sb_msr_config),
    # (f'{base_name}_4_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), nsga2_vessel_sb_msr_config),
    # (f'{base_name}_5_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), nsga2_vessel_sb_msr_config),
    # (f'{base_name}_6_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), nsga2_vessel_sb_msr_config),
    
    # RS-O
    # (f'{base_name}_2_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), scenic_rs_o_config),
    # (f'{base_name}_2_vessel_1_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 1), scenic_rs_o_config),
    (f'{base_name}_3_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), scenic_rs_o_config),
    # (f'{base_name}_3_vessel_1_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 1), scenic_rs_o_config),
    # (f'{base_name}_4_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), scenic_rs_o_config),
    # (f'{base_name}_5_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), scenic_rs_o_config),
    # (f'{base_name}_6_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), scenic_rs_o_config),
    
    #RS-MSR
    # (f'{base_name}_2_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), scenic_rs_msr_config),
    # (f'{base_name}_2_vessel_1_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 1), scenic_rs_msr_config),
    (f'{base_name}_3_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), scenic_rs_msr_config),
    # (f'{base_name}_3_vessel_1_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 1), scenic_rs_msr_config),
    # (f'{base_name}_4_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), scenic_rs_msr_config),
    # (f'{base_name}_5_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), scenic_rs_msr_config),
    # (f'{base_name}_6_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), scenic_rs_msr_config), 
    
]


#----------------------------------------------------------

tests : List[SolverBase] = [SolverFactory.factory(measurement_name=measurement_name,
                                                functional_scenarios=interactions_to_run, test_config=config,
                                                number_of_runs=NUMBER_OF_RUNS[interactions_to_run[0].actor_number_by_type],
                                                warmups=WARMUPS, verbose=VERBOSE)
                            for (measurement_name, interactions_to_run, config) in measurements]


def main():
    processes : List[Process] = []
    for test in tests: 
        process = SceneGenerationProcess(test)
        process.start()
        processes.append(process)

    # Wait for all processes to complete
    for p in processes:
        p.join()
        
        
        
if __name__ == '__main__':
    main()