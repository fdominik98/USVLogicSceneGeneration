from collections import defaultdict
import pprint
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from utils.asv_utils import EPSILON
from evaluation.fishers_exact_odds_ratio import FisherExactOddsRatio
from visualization.plotting_utils import EvalPlot

class SuccessRatePlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], mode='algo'): 
        self.mode = mode
        self.success_rates : Dict[int, Dict[str, List[int]]] = defaultdict(lambda : defaultdict(lambda : []))
        for eval_data in eval_datas:
            if self.mode == 'algo':
                group_key = eval_data.algorithm_desc
            elif self.mode == 'config':
                group_key = eval_data.config_group
            else:
                raise Exception('Unknown grouping mode')
            self.success_rates[eval_data.vessel_number][group_key].append(0 if eval_data.best_fitness_index > 0.0 else 1)
            
        EvalPlot.__init__(self, eval_datas)
        
    def create_fig(self) -> plt.Figure:
        figsize = (10, 4) if self.mode == 'algo' else (6, 3)
        fig, axes = plt.subplots(1, len(self.success_rates), figsize=figsize, gridspec_kw={'width_ratios': [1]*len(self.success_rates)})
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)

        for i, (vessel_num, group_measurements) in enumerate(self.success_rates.items()):
            if self.mode == 'algo':
                labels = self.algo_labels
                colors = self.algo_colors
            elif self.mode == 'config':
                labels = self.group_labels
                colors = self.algo_colors
            else:
                raise Exception('Unknown grouping mode')
            
            percentages = [np.mean(data) * 100 for data in group_measurements.values()]
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes  
            bars : plt.BarContainer = axi.bar(labels, percentages, color=colors, edgecolor='black', linewidth=2)
            axi.set_title(self.vessel_num_labels[i])
            if i == 0:
                axi.set_ylabel('Success rate (%)')
            axi.set_aspect('auto', adjustable='box')
            axi.set_xticks(range(len(labels))) 
            axi.set_xticklabels(labels, rotation=0, ha='right', fontweight='bold')
            if i != 0:
                axi.set_yticks([])
            axi.set_ylim(0, 115)
            
            for i, bar in enumerate(bars):
                axi.text(bar.get_x() + bar.get_width() / 2, 102, 
                f'{len(list(group_measurements.values())[i])}', ha='center', va='bottom', fontsize=10)

        fig.tight_layout()
        return fig
        