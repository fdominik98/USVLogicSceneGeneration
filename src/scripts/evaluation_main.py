from multiprocessing import Process, cpu_count
from typing import List, Tuple

from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.constraint_satisfaction.solver_factory import SolverFactory
from logical_level.models.logical_model_manager import LogicalModelManager
from utils.evaluation_config import MEAS_GlobalConfig, nsga2_vessel_sb_o_config, scenic_rs_o_config, scenic_rs_msr_config, nsga2_vessel_sb_msr_config, nsga3_vessel_sb_msr_config,  nsga3_vessel_sb_o_config
from utils.scenario import Scenario

class SceneGenerationProcess(Process):
    def __init__(self, solver : SolverBase, core_id : int) -> None:
        super().__init__(target=solver.run, args=(core_id,), name=solver.measurement_name, daemon=True)

measurements : List[Tuple[str, List[Scenario], EvaluationData]] = [
    # SB-O
    (f'{MEAS_GlobalConfig.BASE_NAME}_1_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(1, 0), nsga3_vessel_sb_o_config),
    
    # SB-O
    # (f'{MEAS_GlobalConfig.BASE_NAME}_2_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), nsga3_vessel_sb_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_2_vessel_1_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 1), nsga3_vessel_sb_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_3_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), nsga3_vessel_sb_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_3_vessel_1_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 1), nsga3_vessel_sb_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_4_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), nsga3_vessel_sb_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_5_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), nsga3_vessel_sb_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_6_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), nsga3_vessel_sb_o_config),
    
    # # SB-MSR
    # (f'{MEAS_GlobalConfig.BASE_NAME}_2_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), nsga3_vessel_sb_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_2_vessel_1_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 1), nsga3_vessel_sb_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_3_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), nsga3_vessel_sb_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_3_vessel_1_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 1), nsga3_vessel_sb_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_4_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), nsga3_vessel_sb_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_5_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), nsga3_vessel_sb_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_6_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), nsga3_vessel_sb_msr_config),
    
    # RS-O
    # (f'{MEAS_GlobalConfig.BASE_NAME}_2_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), scenic_rs_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_2_vessel_1_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(2, 1), scenic_rs_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_3_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), scenic_rs_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_3_vessel_1_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(3, 1), scenic_rs_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_4_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), scenic_rs_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_5_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), scenic_rs_o_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_6_vessel_0_obstacle_scenarios', LogicalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), scenic_rs_o_config),
    
    #RS-MSR
    # (f'{MEAS_GlobalConfig.BASE_NAME}_2_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), scenic_rs_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_2_vessel_1_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 1), scenic_rs_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_3_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), scenic_rs_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_3_vessel_1_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 1), scenic_rs_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_4_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), scenic_rs_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_5_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), scenic_rs_msr_config),
    # (f'{MEAS_GlobalConfig.BASE_NAME}_6_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), scenic_rs_msr_config), 
    
]


#----------------------------------------------------------

tests : List[SolverBase] = [SolverFactory.factory(measurement_name=measurement_name,
                                                functional_scenarios=interactions_to_run, test_config=config,
                                                number_of_runs=MEAS_GlobalConfig.NUMBER_OF_RUNS[interactions_to_run[0].actor_number_by_type],
                                                warmups=MEAS_GlobalConfig.WARMUPS, verbose=MEAS_GlobalConfig.VERBOSE)
                            for (measurement_name, interactions_to_run, config) in measurements]


def main():
    core_count = cpu_count()
    processes : List[Process] = []
    for i in range(len(tests)):
        process = SceneGenerationProcess(tests[i], i % core_count)
        process.start()
        processes.append(process)

    # Wait for all processes to complete
    for p in processes:
        p.join()
        
        
        
if __name__ == '__main__':
    main()