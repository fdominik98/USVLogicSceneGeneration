import math
import random
from typing import Dict, List
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData


class VesselTypeSampler():
    @staticmethod
    def sample(scenarios : List[MultiLevelScenario], sample_size, distribution : Dict[str, float] = {}) -> List[float]:
        random.shuffle(scenarios)
        sized_distribution = {vessel_type : math.floor(percentage * sample_size / 100) for vessel_type, percentage in distribution.items()}
        result = [0.0, 0.0, 0.0]
        current_distribution = {vessel_type : 0 for vessel_type in distribution.keys()}
        for scenario in scenarios:
            if len(current_distribution) == 0:
                result[0] += len(scenario.functional_scenario.overtaking_interpretation)
                result[1] += len(scenario.functional_scenario.head_on_interpretation)
                result[2] += len(scenario.functional_scenario.crossing_interpretation)
            else:                        
                for vessel in scenario.concrete_scene.non_os:
                    if vessel.vessel_type in sized_distribution and current_distribution[vessel.vessel_type] < sized_distribution[vessel.vessel_type]:
                        current_distribution[vessel.vessel_type] += 1
                        if scenario.functional_scenario.overtaking(scenario.to_object(vessel), None):
                            result[0] += 1
                        elif scenario.functional_scenario.head_on(scenario.to_object(vessel), None):
                            result[1] += 1
                        elif scenario.functional_scenario.crossing(scenario.to_object(vessel), None):
                            result[2] += 1
        achieved_size = sum(current_distribution.values())
        if sample_size != achieved_size:
            print(f'More sample is needed : >{sample_size - achieved_size}')
        achieved_distribution = {vessel_type : size / achieved_size * 100 for vessel_type, size in current_distribution.items()}
        print(achieved_distribution)
        return result