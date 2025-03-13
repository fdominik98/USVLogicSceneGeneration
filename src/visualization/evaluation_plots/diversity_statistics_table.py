import itertools
from typing import List, Tuple
import matplotlib.pyplot as plt
from evaluation.chi_square_kl_div import ChiSquareKLDiv
from evaluation.permutation_evenness_test import PermutationEvennessTest
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from visualization.plotting_utils import DummyEvalPlot
from itertools import combinations

class DiversityStatisticsTable(DummyEvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], get_equivalence_class_distribution=ConcreteSceneAbstractor.get_equivalence_class_distribution): 
        self.get_equivalence_class_distribution = get_equivalence_class_distribution
        super().__init__(eval_datas)
        
    @property   
    def config_groups(self) -> List[str]:
        return ['sb-o', 'sb-msr', 'rs-o', 'rs-msr', 'common_ocean_benchmark']
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        return [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
        
    def create_fig(self) -> plt.Figure:
        groups_to_compare = list(combinations(self.comparison_groups, 2))
        for i, actor_number_by_type in enumerate(self.actor_numbers_by_type):
            for j, (group1, group2) in enumerate(groups_to_compare):
                equivalence_classes1 = self.get_equivalence_class_distribution([eval_data.best_scene for eval_data in self.measurements[actor_number_by_type][group1]], actor_number_by_type)
                equivalence_classes2 = self.get_equivalence_class_distribution([eval_data.best_scene for eval_data in self.measurements[actor_number_by_type][group2]], actor_number_by_type)
                if len(equivalence_classes1) == 0 or len(equivalence_classes2) == 0:
                    continue
                values1 = [int(count) for _, count in equivalence_classes1.values()]
                values2 = [int(count) for _, count in equivalence_classes2.values()]
                if sum(values1) == 0 or sum(values2) == 0:
                    continue
                
                #evenness_test = PermutationEvennessTest(values1, values2)
                #print(f'{vessel_number} vessels, {group1} - {group2}: {group1} evenness={evenness_test.evenness_1}, {group2} evenness={evenness_test.evenness_2}, p-value:{evenness_test.p_value}, effect-size:{evenness_test.observed_diff}')
                
                test = ChiSquareKLDiv(values1, values2)
                print(f'{actor_number_by_type[0]} vessels, {actor_number_by_type[1]} obstacles, {group1} - {group2}: {group1} p-value:{test.p_value}, KL Divergence::{test.kl_div}')

        return DummyEvalPlot.create_fig(self)
        
        
class AmbiguousDiversityStatisticsTable(DiversityStatisticsTable):
    def __init__(self, eval_datas):
        super().__init__(eval_datas, ConcreteSceneAbstractor.get_ambiguous_equivalence_class_distribution)
        
class UnspecifiedDiversityStatisticsTable(DiversityStatisticsTable):
    def __init__(self, eval_datas):
        super().__init__(eval_datas, ConcreteSceneAbstractor.get_unspecified_equivalence_class_distribution)
        