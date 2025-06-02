from multiprocessing import Process, cpu_count
from typing import List, Tuple

from functional_level.metamodels.functional_scenario import FunctionalScenario
from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.msr_constraint_satisfaction import MSRConstraintSatisfaction
from logical_level.constraint_satisfaction.solver_factory import SolverFactory
from utils.evaluation_config import create_config, MSRMeasurementConfig, DummyMeasurementConfig

class SceneGenerationProcess(Process):
    def __init__(self, test : MSRConstraintSatisfaction, core_id : int) -> None:
        super().__init__(target=test.run, args=(core_id,), name=test.measurement_name, daemon=True)


def main():
    SB_MSR = 'SB-MSR'
    RS_MSR = 'RS-MSR'

    measurement_config = MSRMeasurementConfig()
    measurements : List[Tuple[str, List[FunctionalScenario], EvaluationData]] = [
        # # SB-MSR
        (f'{measurement_config.BASE_NAME}_2_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), SB_MSR),
        (f'{measurement_config.BASE_NAME}_3_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), SB_MSR),
        (f'{measurement_config.BASE_NAME}_4_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), SB_MSR),
        (f'{measurement_config.BASE_NAME}_5_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), SB_MSR),
        (f'{measurement_config.BASE_NAME}_6_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), SB_MSR),
        
        #RS-MSR
        (f'{measurement_config.BASE_NAME}_2_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(2, 0), RS_MSR),
        (f'{measurement_config.BASE_NAME}_3_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(3, 0), RS_MSR),
        (f'{measurement_config.BASE_NAME}_4_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(4, 0), RS_MSR),
        (f'{measurement_config.BASE_NAME}_5_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(5, 0), RS_MSR),
        (f'{measurement_config.BASE_NAME}_6_vessel_0_obstacle_scenarios', FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(6, 0), RS_MSR), 
        
    ]


    #----------------------------------------------------------
    tests : List[MSRConstraintSatisfaction] = []

    for i in range(measurement_config.REPETITIONS):
    # for i in range(1):
        for (measurement_name, functional_scenarios, config_group) in measurements:
            config = create_config(measurement_config, config_group, measurement_config.RANDOM_SEED + i)
            tests.append(MSRConstraintSatisfaction(solver=SolverFactory.factory(config.algorithm_desc, measurement_config.VERBOSE),
                                                    measurement_name=measurement_name,
                                                        functional_scenarios=functional_scenarios, test_config=config,
                                                        warmups=measurement_config.WARMUPS,
                                                        average_time_per_scene=measurement_config.AVERAGE_TIME_PER_SCENE,
                                                        verbose=measurement_config.VERBOSE))


    tests.sort(key=lambda x: x.scenarios[0][0].vessel_number)  # Sort by vessel number for better load balancing
    
    
    core_count = cpu_count()
    processes: List[Process] = []
    i = 0
    while i < len(tests):
        # Clean up finished processes
        processes = [p for p in processes if p.is_alive()]
        if len(processes) < core_count:
            process = SceneGenerationProcess(tests[i], i % core_count)
            process.start()
            processes.append(process)
            i += 1
        else:
            # Wait a bit before checking again
            for p in processes:
                p.join(timeout=0.1)
    # Wait for all remaining processes to complete
    for p in processes:
        p.join()
        
        
        
if __name__ == '__main__':
    main()