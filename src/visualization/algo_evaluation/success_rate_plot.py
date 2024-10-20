from collections import defaultdict
import pprint
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.usv_config import EPSILON
from evaluation.fishers_exact_odds_ratio import FisherExactOddsRatio
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot

class SuccessRatePlot(MyPlot):  
    def __init__(self, eval_datas : List[EvaluationData], mode='algo'): 
        self.mode = mode
        self.eval_datas = eval_datas
        self.success_rates : Dict[int, Dict[str, List[int]]] = defaultdict(lambda : defaultdict(lambda : []))
        for eval_data in eval_datas:
            if self.mode == 'algo':
                group_key = eval_data.algorithm_desc
            elif self.mode == 'config':
                group_key = eval_data.config_group
            else:
                raise Exception('Unknown grouping mode')
            self.success_rates[eval_data.vessel_number][group_key].append(0 if eval_data.best_fitness_index > 0.0 else 1)
            
        self.vessel_num_labels = vessel_number_mapper(list(self.success_rates.keys()))
        MyPlot.__init__(self)
        
    def create_fig(self):
        figsize = (10, 4) if self.mode == 'algo' else (6, 3)
        fig, axes = plt.subplots(1, len(self.success_rates), figsize=figsize, gridspec_kw={'width_ratios': [1]*len(self.success_rates)})
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)

        for i, (vessel_num, group_measurements) in enumerate(self.success_rates.items()):
            if self.mode == 'algo':
                group_labels = algo_mapper(list(group_measurements.keys()))
            elif self.mode == 'config':
                group_labels = config_group_mapper(list(group_measurements.keys()))
            else:
                raise Exception('Unknown grouping mode')
            
            percentages = [np.mean(data) * 100 for data in group_measurements.values()]
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes  
            bars : plt.BarContainer = axi.bar(group_labels, percentages, color=group_colors(len(group_labels)), edgecolor='black', linewidth=2)
            axi.set_title(self.vessel_num_labels[i])
            if i == 0:
                axi.set_ylabel('Success rate (%)')
            axi.set_aspect('auto', adjustable='box')
            axi.set_xticks(range(len(group_labels))) 
            axi.set_xticklabels(group_labels, rotation=45, ha='right', fontweight='bold')
            axi.set_ylim(0, 115)
            
            for i, bar in enumerate(bars):
                axi.text(bar.get_x() + bar.get_width() / 2, 102, 
                f'{len(list(group_measurements.values())[i])}', ha='center', va='bottom', fontsize=10)

        fig.tight_layout()