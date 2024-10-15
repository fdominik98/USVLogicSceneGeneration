from collections import defaultdict
import pprint
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.usv_config import EPSILON
from evaluation.fishers_exact_odds_ratio import FisherExactOddsRatio
from evaluation.eqv_class_calculator import EqvClassCalculator
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot

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

        for i, (vessel_num, group_measurements) in enumerate(self.config_data.items()):
            group_labels = config_group_mapper(list(group_measurements.keys()))
            for j, (meas_label, eval_datas) in enumerate(group_measurements.items()):
            
                data = EqvClassCalculator(eval_datas).clause_desc_set
                labels = range(1, len(data.keys()) + 1)
                values = [int(v) for v in data.values()]
                
                if isinstance(axes, np.ndarray):
                    axi : plt.Axes = axes[j][i]
                else:
                    axi : plt.Axes = axes  
                bars : plt.BarContainer = axi.bar(labels, values, color=group_colors, edgecolor='black', linewidth=0.5)
                axi.set_title(self.vessel_num_labels[i])
                axi.set_ylabel('Samples')
                axi.set_aspect('auto', adjustable='box')
                yticks = np.linspace(0, max(values), 6)
                yticks = [int(t) for t in yticks] 
                axi.set_yticks([yticks[0], yticks[-1]] + list(yticks), minor=False) 
                xticks = np.linspace(labels[0], labels[-1], 6)
                xticks = [int(t) for t in xticks] 
                axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False)             
            
            # for i, bar in enumerate(bars):
            #     axi.text(bar.get_x() + bar.get_width() / 2, max(data.values()) + 5, 
            #     f'{len(list(group_measurements.values())[i])}', ha='center', va='bottom', fontsize=12)

        fig.tight_layout()