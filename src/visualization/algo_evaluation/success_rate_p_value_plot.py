from typing import List
import matplotlib.pyplot as plt
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from evaluation.fishers_exact_odds_ratio import FisherExactOddsRatio
from visualization.algo_evaluation.success_rate_plot import SuccessRatePlot
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, config_group_mapper, group_colors

class SuccessRatePValuePlot(SuccessRatePlot):  
    def __init__(self, eval_datas : List[EvaluationData], mode='algo'): 
        SuccessRatePlot.__init__(self, eval_datas, mode)
        
    def create_fig(self):
        fig, axes = plt.subplots(1, len(self.success_rates), figsize=(10, 4), gridspec_kw={'width_ratios': [1]*len(self.success_rates)})
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
            
            if len(group_measurements) != 0:                
                stat_signif = FisherExactOddsRatio({group : value for group, value in zip(group_labels, group_measurements.values())})
                comparisons = [f'{key[0]} - {key[1]}' for key in stat_signif.p_values.keys()]
                p_values = list(stat_signif.p_values.values())
            else:
                comparisons = []
                p_values = []
            
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes  
                
            axi.bar(comparisons, p_values, color=group_colors)
            axi.axhline(y=0.05, color='red', linestyle='--', label='Significance Level (0.05)')
            axi.set_ylabel('P-value')
            axi.legend()

        fig.tight_layout()