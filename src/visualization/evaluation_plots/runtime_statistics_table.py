from itertools import combinations
from typing import List, Tuple
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from evaluation.mann_whitney_u_cliff_delta import MannWhitneyUCliffDelta
from visualization.plotting_utils import DummyEvalPlot

class RuntimeStatisticsTable(DummyEvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData]): 
        super().__init__(eval_datas)
    
    @property   
    def config_groups(self) -> List[str]:
        return ['sb-o', 'sb-msr', 'rs-o', 'rs-msr']
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        return [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
    
    def create_fig(self):
        groups_to_compare = list(combinations(self.comparison_groups, 2))
        for i, actor_number_by_type in enumerate(self.actor_numbers_by_type):
            for j, (group1, group2) in enumerate(groups_to_compare):            
                values1 = [eval_data.evaluation_time for eval_data in self.measurements[actor_number_by_type][group1]]
                values2 = [eval_data.evaluation_time for eval_data in self.measurements[actor_number_by_type][group2]]
                if len(values1) == 0 or len(values2) == 0:
                    continue
                
                statistical_test = MannWhitneyUCliffDelta(values1, values2)
                print(f'{actor_number_by_type[0]} vessels, {actor_number_by_type[1]} obstacles, {group1} - {group2}: p-value:{statistical_test.p_value_mann_w}, effect-size:{statistical_test.effect_size_cohens_d}')
            
        return DummyEvalPlot.create_fig(self)