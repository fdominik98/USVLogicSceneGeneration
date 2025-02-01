from typing import List
import matplotlib.pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from visualization.plotting_utils import EvalPlot

class DiversityPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], get_equivalence_class_distribution=ConcreteSceneAbstractor.get_equivalence_class_distribution): 
        self.get_equivalence_class_distribution = get_equivalence_class_distribution
        super().__init__(eval_datas)
        
    
    @property   
    def config_groups(self) -> List[str]:
        return ['SBO', 'scenic_distribution', 'common_ocean_benchmark']
    
    @property
    def vessel_numbers(self) -> List[int]:
        return [2, 3, 4, 5, 6]
        
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(self.comparison_group_count, self.vessel_num_count, figsize=(3 * 4, 5), constrained_layout=True)
        axes = np.atleast_2d(axes)
        fig.subplots_adjust(wspace=0.5)
        fig.subplots_adjust(hspace=0.5)
        
        for i, label in enumerate(reversed(self.group_labels)):
            fig.text(0.5, 0.05 + i * 0.3, label, ha='center', va='center', fontsize=12, fontweight='bold')

        for i, vessel_number in enumerate(self.vessel_numbers):
            for j, config_group in enumerate(self.config_groups):
                axi : plt.Axes = axes[j][i]
                if j == 0:
                    axi.set_title(self.vessel_num_labels[i])
                self.init_axi(i, axi, 'Samples')
                
                equivalence_classes = self.get_equivalence_class_distribution([eval_data.best_scene for eval_data in self.measurements[vessel_number][config_group]], vessel_number)
                if len(equivalence_classes) == 0:
                    continue
                equivalence_classes = dict(sorted(equivalence_classes.items(), key=lambda item: item[1][1], reverse=True))
                values = [int(count) for _, count in equivalence_classes.values()]
                if sum(values) == 0:
                    continue
                
                labels = range(1, len(equivalence_classes.keys()) + 1)
                bars : plt.BarContainer = axi.bar(labels, values, color=self.colors[j], edgecolor='black', linewidth=0)
                
                xticks = np.linspace(labels[0], labels[-1], 6)
                xticks = [int(t) for t in xticks] 
                axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False) 
                self.set_yticks(axi, values)
                
                axi.text(0.98, 0.98, self.get_shape_coverage_text(equivalence_classes), 
                transform=axi.transAxes,  # Use axis coordinates
                verticalalignment='top', # Align text vertically to the top
                horizontalalignment='right',
                fontsize=11,
                fontweight='bold')

        return fig
        
    def get_shape_coverage_text(self, equivalence_classes : dict) -> str:
        found_length = sum(1 for _, count in equivalence_classes.values() if count > 0)
        coverage_percent = found_length/len(equivalence_classes)*100 if len(equivalence_classes) != 0 else 0
        return f'covered shapes: {found_length}/{len(equivalence_classes)}\n{coverage_percent:.1f}%'
        
class AmbiguousDiversityPlot(DiversityPlot):
    def __init__(self, eval_datas):
        super().__init__(eval_datas, ConcreteSceneAbstractor.get_ambiguous_equivalence_class_distribution)
        
class UnspecifiedDiversityPlot(DiversityPlot):
    def __init__(self, eval_datas):
        super().__init__(eval_datas, ConcreteSceneAbstractor.get_unspecified_equivalence_class_distribution)
        
    def get_shape_coverage_text(self, equivalence_classes : dict) -> str:
        found_length = sum(1 for _, count in equivalence_classes.values() if count > 0)
        return f'covered shapes: {found_length}/?'