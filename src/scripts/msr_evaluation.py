from multiprocessing import Process, cpu_count
from typing import List, Tuple

from functional_level.metamodels.functional_scenario import FunctionalScenario
from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.msr_constraint_satisfaction import MSRConstraintSatisfaction
from logical_level.constraint_satisfaction.solver_factory import SolverFactory
from utils.evaluation_config import create_config, MSRMeasurementConfig, DummyMeasurementConfig

measurement_config = MSRMeasurementConfig()
search_sb_msr_config = create_config(measurement_config, 'SB-MSR')
scenic_rs_msr_config = create_config(measurement_config, 'RS-MSR')

class SceneGenerationProcess(Process):
    def __init__(self, solver : MSRConstraintSatisfaction, core_id : int) -> None:
        super().__init__(target=solver.run, args=(core_id,), name=solver.measurement_name, daemon=True)

measurements : List[Tuple[str, List[FunctionalScenario], EvaluationData]] = [
    # # SB-MSR
    (f'{measurement_config.BASE_NAME}_2_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), search_sb_msr_config),
    (f'{measurement_config.BASE_NAME}_3_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), search_sb_msr_config),
    (f'{measurement_config.BASE_NAME}_4_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), search_sb_msr_config),
    (f'{measurement_config.BASE_NAME}_5_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), search_sb_msr_config),
    (f'{measurement_config.BASE_NAME}_6_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), search_sb_msr_config),
    
    #RS-MSR
    (F'{measurement_config.BASE_NAME}_2_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), scenic_rs_msr_config),
    (f'{measurement_config.BASE_NAME}_3_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), scenic_rs_msr_config),
    (f'{measurement_config.BASE_NAME}_4_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), scenic_rs_msr_config),
    (f'{measurement_config.BASE_NAME}_5_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), scenic_rs_msr_config),
    (f'{measurement_config.BASE_NAME}_6_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), scenic_rs_msr_config), 
    
]


#----------------------------------------------------------

tests : List[MSRConstraintSatisfaction] = [MSRConstraintSatisfaction(solver=SolverFactory.factory(config.algorithm_desc, measurement_config.VERBOSE),
                                                               measurement_name=measurement_name,
                                                                functional_scenarios=interactions_to_run, test_config=config,
                                                                warmups=measurement_config.WARMUPS, verbose=measurement_config.VERBOSE)
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