from collections import defaultdict
import pprint
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.usv_config import EPSILON
from evaluation.mann_whitney_u_cliff_delta import MannWhitneyUCliffDelta
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot

class EvalTimePlot(MyPlot):  
    def __init__(self, eval_datas : List[EvaluationData], all=False, mode='algo'): 
        self.mode = mode
        self.all = all
        self.eval_datas = eval_datas
        self.runtimes : Dict[int, Dict[str, List[float]]] = defaultdict(lambda : defaultdict(lambda : []))
        for eval_data in eval_datas:
            if self.mode == 'algo':
                group_key = eval_data.algorithm_desc
            elif self.mode == 'config':
                group_key = eval_data.config_group
            else:
                raise Exception('Unknown grouping mode')
            if eval_data.best_fitness_index == 0.0 or all:     
                self.runtimes[eval_data.vessel_number][group_key].append(eval_data.evaluation_time)
            else: 
                self.runtimes[eval_data.vessel_number][group_key] = self.runtimes[eval_data.vessel_number][group_key]
            
        self.vessel_num_labels = vessel_number_mapper(list(self.runtimes.keys()))
        MyPlot.__init__(self)
        
    def create_fig(self):
        figsize = (10, 4) if self.mode == 'algo' else (6, 3)
        fig, axes = plt.subplots(1, len(self.runtimes), figsize=figsize, gridspec_kw={'width_ratios': [1]*len(self.runtimes)})
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)

        for i, (vessel_num, group_measurements) in enumerate(self.runtimes.items()):
            if self.mode == 'algo':
                group_labels = algo_mapper(list(group_measurements.keys()))
            elif self.mode == 'config':
                group_labels = config_group_mapper(list(group_measurements.keys()))
            else:
                raise Exception('Unknown grouping mode')
            
            data = list(group_measurements.values())
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes     
            violinplot = axi.violinplot(data, widths=0.7, showmeans=True, showmedians=True)
            axi.set_title(self.vessel_num_labels[i])
            if i == 0:
                axi.set_ylabel('Runtime (s)')
            else:
                axi.set_yticks([])
            axi.set_aspect('auto', adjustable='box')
            #axi.set_yticks(range(max([max(d) for d in data])))
            axi.set_xticks(range(1, len(group_labels)+1), group_labels)
            axi.set_xticklabels(group_labels, rotation=45, ha='right', fontweight='bold')            
            
            for patch, color in zip(violinplot['bodies'], group_colors(len(group_labels))):
                patch.set_facecolor(color)           # Set fill color
                patch.set_linewidth(1.0)   
            
            violinplot['cmeans'].set_color('black')
            violinplot['cmeans'].set_linewidth(2)
            violinplot['cmedians'].set_color('grey')
            violinplot['cmedians'].set_linewidth(2)
            violinplot['cmedians'].set_linestyle(':')
            
            maxy = axi.get_ylim()[1]
            axi.set_ylim(0, maxy*1.15)
                    
            # Annotate each box with the number of samples
            for i, group in enumerate(data, 1):  # '1' because boxplot groups start at 1
                sample_size = len(group)
                axi.text(i, maxy*1.05, f'{sample_size}', ha='center', va='center', fontsize=10, horizontalalignment='center')                   
                    
            

        fig.tight_layout()