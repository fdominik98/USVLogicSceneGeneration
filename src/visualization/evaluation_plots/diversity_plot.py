from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from visualization.plotting_utils import EvalPlot

class DiversityPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], get_equivalence_class_distribution=ConcreteSceneAbstractor.get_equivalence_class_distribution): 
        self.get_equivalence_class_distribution = get_equivalence_class_distribution
        super().__init__(eval_datas)
        
    
    @property   
    def config_groups(self) -> List[str]:
        return ['sb-o', 'sb-msr', 'rs-o', 'rs-msr', 'common_ocean_benchmark']
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        return [(2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (5, 0), (6, 0)]
        
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(self.comparison_group_count, self.vessel_num_count, figsize=(3 * 4, 3.8), constrained_layout=True)
        axes = np.atleast_2d(axes)
        
        for i, actor_number_by_type in enumerate(self.actor_numbers_by_type):
            for j, config_group in enumerate(self.comparison_groups):
                axi : plt.Axes = axes[j][i]
                if j == 0:
                    axi.set_title(self.vessel_num_labels[i])                    
                self.init_axi(i, axi, r"$\bf{" + self.group_labels[j] + r"}$")
                
                equivalence_classes : Dict[int, Tuple[MultiLevelScenario, int]] = self.get_equivalence_class_distribution([eval_data.best_scene for eval_data in self.measurements[actor_number_by_type][config_group]])
                equivalence_classes = dict(sorted(equivalence_classes.items(), key=lambda item: item[1][1], reverse=True))
                values = [int(count) for _, count in equivalence_classes.values()]
                
                all_shapes = len(equivalence_classes)
                relevant_shapes = sum(1 for scenario, count in equivalence_classes.values() if scenario.functional_scenario.is_relevant)
                ambiguous_shapes = sum(1 for scenario, count in equivalence_classes.values() if scenario.functional_scenario.is_ambiguous)
                
                axi.text(0.98, 0.98, f'all shapes: {all_shapes}\nrelevant shapes: {relevant_shapes}\nambiguous shapes: {ambiguous_shapes}', 
                transform=axi.transAxes,  # Use axis coordinates
                verticalalignment='top', # Align text vertically to the top
                horizontalalignment='right',
                fontsize=11,
                fontweight='bold')
                
                if sum(values) == 0:
                    continue
                
                labels = range(1, len(equivalence_classes.keys()) + 1)
                bars : plt.BarContainer = axi.bar(labels, values, color=self.colors[j], edgecolor='black', linewidth=0)
                
                xticks = list(np.linspace(labels[0], labels[-1], 6))
                xticks = [int(t) for t in xticks] 
                axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False) 
                self.set_yticks(axi, values)
                
        return fig

        
class AmbiguousDiversityPlot(DiversityPlot):
    def __init__(self, eval_datas):
        super().__init__(eval_datas)
        
