from typing import List
import matplotlib.pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from evaluation.fishers_exact_odds_ratio import FisherExactOddsRatio
from visualization.algo_evaluation.success_rate_plot import SuccessRatePlot
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, config_group_mapper

class SuccessRateOddsRatioPlot(SuccessRatePlot):  
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
                comparisons = [f'{key[0]} - {key[1]}' for key in stat_signif.odds_ratios.keys()]
                odds_ratios = list(stat_signif.odds_ratios.values())
            else:
                comparisons = []
                odds_ratios = []
            
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes  
            axi.errorbar(odds_ratios, comparisons,
                        fmt='o', capsize=5, label='Odds Ratio', color='blue')
            axi.set_xticklabels(axi.get_xticks(), fontweight='bold')
            axi.axvline(x=1, color='gray', linestyle='--', label='No Association (Odds Ratio = 1)')
            axi.set_xlabel('Odds Ratio')
            axi.legend()
            

        fig.tight_layout()