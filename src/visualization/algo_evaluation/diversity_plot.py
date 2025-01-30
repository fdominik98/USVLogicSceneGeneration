from collections import defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from visualization.algo_evaluation.algo_eval_utils import config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot

class DiversityPlot(MyPlot):  
    def __init__(self, eval_datas : List[EvaluationData], get_equivalence_class_distribution=ConcreteSceneAbstractor.get_equivalence_class_distribution): 
        self.eval_datas = eval_datas
        
        self.get_equivalence_class_distribution = get_equivalence_class_distribution
        
        self.config_data : Dict[int, Dict[str, List[EvaluationData]]] = defaultdict(lambda : defaultdict(lambda : []))
        for eval_data in eval_datas:
            group_key = eval_data.config_group
            if eval_data.best_fitness_index == 0:    
                self.config_data[eval_data.vessel_number][group_key].append(eval_data)               
            
        self.vessel_num_labels = vessel_number_mapper(list(self.config_data.keys()))
        
        MyPlot.__init__(self)
        
        
    def create_fig(self):
        fig, axes = plt.subplots(2, 2, figsize=(2 * 3, 4))
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)
        
        fig.text(0.5, 0.5, 'SBO', ha='center', va='center', fontsize=12, fontweight='bold')
        fig.text(0.5, 0.05, 'Scenic', ha='center', va='center', fontsize=12, fontweight='bold')

        for i, (vessel_num, group_measurements) in enumerate(self.config_data.items()):
            group_labels = config_group_mapper(list(group_measurements.keys()))            
            colors = group_colors(len(group_labels))
            
            for j, (meas_label, eval_datas) in enumerate(group_measurements.items()):
                equivalence_classes = self.get_equivalence_class_distribution([eval_data.best_scene for eval_data in eval_datas], vessel_num)
                equivalence_classes = dict(sorted(equivalence_classes.items(), key=lambda item: item[1][1], reverse=True))
                labels = range(1, len(equivalence_classes.keys()) + 1)
                values = [int(count) for _, count in equivalence_classes.values()]
                
                if isinstance(axes, np.ndarray):
                    axi : plt.Axes = axes[j][i]
                else:
                    axi : plt.Axes = axes  
                bars : plt.BarContainer = axi.bar(labels, values, color=colors[j], edgecolor='black', linewidth=0)
                if j == 0:
                    axi.set_title(self.vessel_num_labels[i])
                if i == 0:
                    axi.set_ylabel('Samples')
                axi.set_aspect('auto', adjustable='box')
                yticks = np.linspace(0, max(values), 6)
                yticks = [int(t) for t in yticks] 
                axi.set_yticks([yticks[0], yticks[-1]] + list(yticks), minor=False) 
                xticks = np.linspace(labels[0], labels[-1], 6)
                xticks = [int(t) for t in xticks] 
                axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False)             
                axi.text(0.98, 0.98, self.get_shape_coverage_text(equivalence_classes), 
                transform=axi.transAxes,  # Use axis coordinates
                verticalalignment='top', # Align text vertically to the top
                horizontalalignment='right',
                fontsize=11,
                fontweight='bold')

        fig.tight_layout(rect=[0, 0.04, 1, 1])
        
    def get_shape_coverage_text(self, equivalence_classes : dict) -> str:
        found_length = sum(1 for _, count in equivalence_classes.values() if count > 0)
        coverage_percent = found_length/len(equivalence_classes)*100
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