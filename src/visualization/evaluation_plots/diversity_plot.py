from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from visualization.plotting_utils import EvalPlot

class DiversityPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], get_equivalence_class_distribution=ConcreteSceneAbstractor.get_equivalence_class_distribution): 
        self.get_equivalence_class_distribution = get_equivalence_class_distribution
        super().__init__(eval_datas)
        
    
    @property   
    def config_groups(self) -> List[str]:
        return ['SBO', 'scenic_distribution']
    
    @property
    def vessel_numbers(self) -> List[int]:
        return [2, 3, 4, 5, 6]
        
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(self.comparison_group_count, self.vessel_num_count, figsize=(3 * 4, 3.8), constrained_layout=True)
        axes = np.atleast_2d(axes)
        
        for i, vessel_number in enumerate(self.vessel_numbers):
            for j, config_group in enumerate(self.comparison_groups):
                axi : plt.Axes = axes[j][i]
                if j == 0:
                    axi.set_title(self.vessel_num_labels[i])                    
                self.init_axi(i, axi, r"$\bf{" + self.group_labels[j] + r"}$")
                
                equivalence_classes : Dict[int, Tuple[FunctionalScenario, int]] = self.get_equivalence_class_distribution([eval_data.best_scene for eval_data in self.measurements[vessel_number][config_group]], vessel_number)
                equivalence_classes = dict(sorted(equivalence_classes.items(), key=lambda item: item[1][1], reverse=True))
                values = [int(count) for _, count in equivalence_classes.values()]
                
                irrelevant_classes = [int(count) for e_class, count in equivalence_classes.values() if (len(e_class.overtaking_interpretation) + len(e_class.crossing_interpretation) + len(e_class.head_on_interpretation) / 2) < vessel_number-1]
                print(f'{vessel_number} vessels, {config_group}: irrelevant classes: {sum(irrelevant_classes)}')
                
                
                axi.text(0.98, 0.98, self.get_shape_coverage_text(values), 
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
        
    def get_shape_coverage_text(self, values : List[int]) -> str:
        sample_num = sum(values)
        if sample_num == 0:
            return f'\ncovered shapes: {0}/{len(values)}\n{0}%'
        found_length = sum(1 for value in values if value > 0)
        coverage_percent = found_length/len(values)*100 if len(values) != 0 else 0
        return f'covered shapes: {found_length}/{len(values)}\n{coverage_percent:.1f}%'
        
class AmbiguousDiversityPlot(DiversityPlot):
    def __init__(self, eval_datas):
        super().__init__(eval_datas, ConcreteSceneAbstractor.get_ambiguous_equivalence_class_distribution)
        
class UnspecifiedDiversityPlot(DiversityPlot):
    def __init__(self, eval_datas):
        super().__init__(eval_datas, ConcreteSceneAbstractor.get_unspecified_equivalence_class_distribution)
        
    def get_shape_coverage_text(self, values : List[int]) -> str:
        sample_num = sum(values)
        found_length = sum(1 for value in values if value > 0)
        return f'total samples: {sample_num}\ncovered shapes: {found_length}/?'