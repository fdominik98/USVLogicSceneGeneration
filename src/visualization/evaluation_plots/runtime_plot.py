from typing import List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from visualization.plotting_utils import EvalPlot

class RuntimePlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], is_all=False, is_algo=False): 
        EvalPlot.__init__(self, eval_datas, is_algo=is_algo, is_all=is_all)
    
    @property
    def algos(self) -> List[Tuple[str, str]]:
        return [('nsga2', 'all'), ('nsga2', 'vessel'), ('nsga2', 'category'), ('nsga3', 'all'), ('nsga3', 'vessel'), ('nsga3', 'category'), ('ga', 'all'), ('de', 'all'), ('pso', 'all_swarm')]
        
    @property   
    def config_groups(self) -> List[str]:
        return ['SBO', 'scenic_distribution'] 
    
    @property
    def vessel_numbers(self) -> List[int]:
        return [2, 3, 4, 5, 6]   
    
    def create_fig(self):
        fig, axes = plt.subplots(1, self.vessel_num_count, figsize=(self.vessel_num_count, 4), gridspec_kw={'width_ratios': [1]*self.vessel_num_count}, constrained_layout=True)
        axes = np.atleast_1d(axes)
        
        for i, vessel_number in enumerate(self.vessel_numbers):
            axi : plt.Axes = axes[i]
            axi.set_title(self.vessel_num_labels[i])
            self.init_axi(i, axi, 'Runtime (s)')
            
            data = []
            new_group_labels = []
            for measurement, label in zip(self.measurements[vessel_number].values(), self.group_labels):
                values = [eval_data.evaluation_time for eval_data in measurement]
                if len(values) != 0:
                    data.append(values)
                    new_group_labels.append(label)
                    print(f'{vessel_number} vessels, {label}: median: {np.median(values)} , mean: {np.mean(values)}')
            
            if len(data) == 0:
                continue
            
            violin_plot = axi.violinplot(data, widths=0.7, showmeans=True, showmedians=True)
            
            axi.set_xticks(range(1, len(new_group_labels)+1), new_group_labels)
            axi.set_xticklabels(new_group_labels, rotation=0, ha='right', fontweight='bold')            
            self.set_yticks(axi, range(round(max([max(d) for d in data]))))
            
            for patch, color in zip(violin_plot['bodies'], self.colors):
                patch.set_facecolor(color)           # Set fill color
                patch.set_linewidth(1.0)   
            
            violin_plot['cmeans'].set_color('black')
            violin_plot['cmeans'].set_linewidth(2)
            violin_plot['cmedians'].set_color('grey')
            violin_plot['cmedians'].set_linewidth(2)
            violin_plot['cmedians'].set_linestyle(':')
            
            maxy = axi.get_ylim()[1]
            axi.set_ylim(0, maxy*1.1)
            
                    
            # Annotate each box with the number of samples
            for j, group in enumerate(data, 1):  # '1' because boxplot groups start at 1
                axi.text(j, maxy*1.02, f'{len(group)}', ha='center', va='center', fontsize=10, horizontalalignment='center')  
                                 
        return fig