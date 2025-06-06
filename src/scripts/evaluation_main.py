from multiprocessing import Process, cpu_count
from typing import List, Tuple

from logical_level.constraint_satisfaction.csp_evaluation.csp_evaluator import CSPEvaluatorImpl
from logical_level.constraint_satisfaction.csp_evaluation.csp_scheduler import CSPScheduler, CSPSchedulerFactory
from logical_level.constraint_satisfaction.csp_evaluation.csp_solver_factory import CPSSolverFactory
from utils.evaluation_config import TS_CD_RS, TS_RS, SB_MSR, RS, SB_BASE, BaseSBMeasurementConfig, MeasurementConfig, create_config, RSMeasurementConfig, MSRMeasurementConfig, DummyMeasurementConfig, get_scenarios

class SceneGenerationProcess(Process):
    def __init__(self, test : CSPScheduler, core_id : int, measurement_name) -> None:
        super().__init__(target=test.run, args=(core_id,), name=f'process on {core_id} - {measurement_name}', daemon=True)


def main():
    msr_measurement_config = MSRMeasurementConfig()
    base_sb_measurement_config = BaseSBMeasurementConfig()
    base_rs_measurement_config = RSMeasurementConfig()
    
    measurements : List[Tuple[MeasurementConfig, Tuple[int, int], str]] = [
        # (msr_measurement_config, (2, 0), SB_MSR),
        # (msr_measurement_config, (3, 0), SB_MSR),
        # (msr_measurement_config, (4, 0), SB_MSR),
        # (msr_measurement_config, (5, 0), SB_MSR),
        # (msr_measurement_config, (6, 0), SB_MSR),
        
        # (msr_measurement_config, (2, 0), TS_CD_RS),
        # (msr_measurement_config, (3, 0), TS_CD_RS),
        # (msr_measurement_config, (4, 0), TS_CD_RS),
        # (msr_measurement_config, (5, 0), TS_CD_RS),
        # (msr_measurement_config, (6, 0), TS_CD_RS), 
        
        # (base_measurement_config, (2, 0), SB_BASE),
        # (base_measurement_config, (3, 0), SB_BASE),
        # (base_measurement_config, (4, 0), SB_BASE),
        # (base_measurement_config, (5, 0), SB_BASE),
        # (base_measurement_config, (6, 0), SB_BASE), 
        
        # (base_rs_measurement_config, (2, 0), RS),
        # (base_rs_measurement_config, (3, 0), RS),
        # (base_rs_measurement_config, (4, 0), RS),
        # (base_rs_measurement_config, (5, 0), RS),
        # (base_rs_measurement_config, (6, 0), RS), 
        
        (base_rs_measurement_config, (2, 0), TS_RS),
        (base_rs_measurement_config, (3, 0), TS_RS),
        (base_rs_measurement_config, (4, 0), TS_RS),
        (base_rs_measurement_config, (5, 0), TS_RS),
        (base_rs_measurement_config, (6, 0), TS_RS), 
    ]


    #----------------------------------------------------------
    tests : List[Tuple[CSPScheduler, str, int]] = []

    for i in range(1):  # Repeat the measurements 30 times
    # for i in range(1):
        for (measurement_config, actor_number, config_group) in measurements:
            random_seed = measurement_config.RANDOM_SEED + i
            measurement_name = f'{measurement_config.BASE_NAME}_{actor_number[0]}_vessel_{actor_number[1]}_obstacle_scenarios'
            config = create_config(measurement_config, config_group, random_seed)
            solver = CPSSolverFactory.factory(config.algorithm_desc, measurement_config.VERBOSE)
            
            evaluator = CSPEvaluatorImpl(solver, measurement_name, config, measurement_config.VERBOSE)
            
            scenarios = get_scenarios(actor_number[0], actor_number[1], config_group)
            
            scheduler = CSPSchedulerFactory.factory(evaluator, scenarios, random_seed, measurement_config.WARMUPS,
                                                    measurement_config.AVERAGE_TIME_PER_SCENE, config.init_method)
            
            tests.append((scheduler, measurement_name, actor_number[0]))


    tests.sort(key=lambda x: x[2])  # Sort by vessel number for better load balancing
    
    
    core_count = cpu_count()
    processes: List[Process] = []
    i = 0
    while i < len(tests):
        # Clean up finished processes
        processes = [p for p in processes if p.is_alive()]
        if len(processes) < core_count:
            process = SceneGenerationProcess(tests[i][0], i % core_count, tests[i][1])
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