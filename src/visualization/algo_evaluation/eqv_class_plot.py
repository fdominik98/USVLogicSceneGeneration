from collections import defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from evaluation.eqv_class_calculator import EqvClassCalculator
from visualization.algo_evaluation.algo_eval_utils import config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot
from model.environment.functional_models.usv_env_desc_list import MSR_EQUIV_CLASSES

class EqvClassPlot(MyPlot):  
    def __init__(self, eval_datas : List[EvaluationData]): 
        self.eval_datas = eval_datas
        self.config_data : Dict[int, Dict[str, List[EvaluationData]]] = defaultdict(lambda : defaultdict(lambda : []))
        for eval_data in eval_datas:
            group_key = eval_data.config_group
            if eval_data.best_fitness_index == 0:    
                self.config_data[eval_data.vessel_number][group_key].append(eval_data)               
            
        self.vessel_num_labels = vessel_number_mapper(list(self.config_data.keys()))
        
        MyPlot.__init__(self)
        
    def create_fig(self):
        vessel_num_count = len(self.config_data)
        fig, axes = plt.subplots(2, vessel_num_count, figsize=(vessel_num_count * 3, 4))
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)
        
        fig.text(0.5, 0.5, 'MSR', ha='center', va='center', fontsize=12, fontweight='bold')
        fig.text(0.5, 0.05, 'SBO', ha='center', va='center', fontsize=12, fontweight='bold')

        for i, (vessel_num, group_measurements) in enumerate(self.config_data.items()):
            group_labels = config_group_mapper(list(group_measurements.keys()))            
            colros = group_colors(len(group_labels))
            
            for j, (meas_label, eval_datas) in enumerate(group_measurements.items()):
                data = EqvClassCalculator().get_equivalence_classes(eval_datas)
                found_length = len(data)
                for equiv_class in MSR_EQUIV_CLASSES[vessel_num]:
                    ass_clause = equiv_class.get_asymmetric_clause()
                    ass_clause.remove_non_ego_ralations()
                    if ass_clause not in data:
                        data[ass_clause] = 0
                data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
                labels = range(1, len(data.keys()) + 1)
                values = [int(v) for v in data.values()]
                
                if isinstance(axes, np.ndarray):
                    axi : plt.Axes = axes[j][i]
                else:
                    axi : plt.Axes = axes  
                bars : plt.BarContainer = axi.bar(labels, values, color=colros[j], edgecolor='black', linewidth=0)
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
            
                coverage_percent = found_length/len(data)*100
                axi.text(0.98, 0.98, f'covered shapes: {found_length}/{len(data)}\n{coverage_percent:.1f}%', 
                transform=axi.transAxes,  # Use axis coordinates
                verticalalignment='top', # Align text vertically to the top
                horizontalalignment='right',
                fontsize=11)

        fig.tight_layout(rect=[0, 0.04, 1, 1])