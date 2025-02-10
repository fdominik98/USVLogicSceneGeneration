from itertools import combinations
from typing import List
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from evaluation.mann_whitney_u_cliff_delta import MannWhitneyUCliffDelta
from visualization.plotting_utils import DummyEvalPlot

class RuntimeStatisticsTable(DummyEvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData]): 
        super().__init__(eval_datas)
    
    @property   
    def config_groups(self) -> List[str]:
        return ['SBO', 'scenic_distribution']
    
    @property
    def vessel_numbers(self) -> List[int]:
        return [2, 3, 4, 5, 6]
    
    def create_fig(self):
        groups_to_compare = list(combinations(self.comparison_groups, 2))
        for i, vessel_number in enumerate(self.vessel_numbers):
            for j, (group1, group2) in enumerate(groups_to_compare):            
                values1 = [eval_data.evaluation_time for eval_data in self.measurements[vessel_number][group1]]
                values2 = [eval_data.evaluation_time for eval_data in self.measurements[vessel_number][group2]]
                if len(values1) == 0 or len(values2) == 0:
                    continue
                
                statistical_test = MannWhitneyUCliffDelta(values1, values2)
                print(f'{vessel_number} vessels, {group1} - {group2}: p-value:{statistical_test.p_value_mann_w}, effect-size:{statistical_test.effect_size_cohens_d}')
            
        return DummyEvalPlot.create_fig(self)