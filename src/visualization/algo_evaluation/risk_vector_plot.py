from collections import defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from asv_utils import EPSILON
from visualization.algo_evaluation.algo_eval_utils import config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot

class RiskVectorPlot(MyPlot):  
    metric_map_index = {
        'dcpa' : 0,
        'tcpa' : 1,
        'ds' : 2,
        'proximity' : 3,
    }
    
    metric_map_title = {
        'dcpa' : r'DCPA of OS to closest TS (s)',
        'tcpa' : r'TCPA of OS to closest TS (s)',
        'ds' : r'DS index of OS at $t_0$',
        'proximity' : r'Max proximity index of OS at $t_0$',
    }
    
    metric_map_max = {
        'dcpa' : 200,
        'tcpa' : 1500,
        'ds' : 1.0,
        'proximity' : 1.0,
    }
    
    
    def __init__(self, eval_datas : List[EvaluationData], metric = 'dcpa'): 
        self.metric = metric
        self.eval_datas = eval_datas
        self.risk_indices : Dict[int, Dict[str, List[float]]] = defaultdict(lambda : defaultdict(lambda : []))
        for eval_data in eval_datas:
            if eval_data.best_fitness_index == 0.0:                
                if eval_data.risk_vector == None:
                    raise Exception('None vector found among optimal solutions')
                data = eval_data.risk_vector[self.metric_map_index[metric]]
                self.risk_indices[eval_data.vessel_number][eval_data.config_group].append(data)
            else: 
                self.risk_indices[eval_data.vessel_number][eval_data.config_group] = self.risk_indices[eval_data.vessel_number][eval_data.config_group]
            
        self.vessel_num_labels = vessel_number_mapper(list(self.risk_indices.keys()))
        MyPlot.__init__(self)
        
        
    def create_fig(self):
        figsize = (6, 3)
        fig, axes = plt.subplots(1, len(self.risk_indices), figsize=figsize, gridspec_kw={'width_ratios': [1]*len(self.risk_indices)})
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)

        for i, (vessel_num, group_measurements) in enumerate(self.risk_indices.items()):
            group_labels = config_group_mapper(list(group_measurements.keys()))
            data = list(group_measurements.values())
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes     
            violinplot = axi.violinplot(data, widths=0.7, showmeans=True, showmedians=True)
            axi.set_title(self.vessel_num_labels[i])
            if i == 0:
                axi.set_ylabel(self.metric_map_title[self.metric], fontsize=11)
            if i != 0:
                axi.set_yticks([])
            axi.set_aspect('auto', adjustable='box')
            #axi.set_yticks(range(max([max(d) for d in data])))
            axi.set_xticks(range(1, len(group_labels)+1), group_labels)
            axi.set_xticklabels(group_labels, rotation=0, ha='right', fontweight='bold')            
            
            for patch, color in zip(violinplot['bodies'], group_colors(len(group_labels))):
                patch.set_facecolor(color)           # Set fill color
                patch.set_linewidth(1.5)   
            
            violinplot['cmeans'].set_color('black')
            violinplot['cmeans'].set_linewidth(2)
            violinplot['cmedians'].set_color('grey')
            violinplot['cmedians'].set_linewidth(2)
            violinplot['cmedians'].set_linestyle(':')
            
            axi.set_ylim(0, self.metric_map_max[self.metric] * 1.15)
                    
            # Annotate each box with the number of samples
            for i, group in enumerate(data, 1):  # '1' because boxplot groups start at 1
                sample_size = len(group)
                axi.text(i, self.metric_map_max[self.metric]*1.05, f'{sample_size}', ha='center', va='center', fontsize=10, horizontalalignment='center')                   
                    

        fig.tight_layout()