from collections import defaultdict
import pprint
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.usv_config import EPSILON
from model.environment.usv_environment import USVEnvironment
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST
from evaluation.risk_evaluation import RiskVector
from evaluation.mann_whitney_u_cliff_delta import MannWhitneyUCliffDelta
from visualization.algo_evaluation.algo_eval_utils import config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot

class RiskVectorPlot(MyPlot):  
    def __init__(self, eval_datas : List[EvaluationData]): 
        self.eval_datas = eval_datas
        self.risk_vectors : Dict[int, Dict[str, List[float]]] = defaultdict(lambda : defaultdict(lambda : []))
        for eval_data in eval_datas:
            if eval_data.best_fitness_index == 0.0:                
                if eval_data.risk_distance == None:
                    raise Exception('None vector found among optimal solutions')
                self.risk_vectors[eval_data.vessel_number][eval_data.config_group].append(eval_data.risk_distance)
            else: 
                self.risk_vectors[eval_data.vessel_number][eval_data.config_group] = self.risk_vectors[eval_data.vessel_number][eval_data.config_group]
            
        self.vessel_num_labels = vessel_number_mapper(list(self.risk_vectors.keys()))
        MyPlot.__init__(self)
        
        
    def create_fig(self):
        fig, axes = plt.subplots(1, len(self.risk_vectors), figsize=(10, 4), gridspec_kw={'width_ratios': [1]*len(self.risk_vectors)})
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)

        for i, (vessel_num, group_measurements) in enumerate(self.risk_vectors.items()):
            group_measurements = dict(sorted(group_measurements.items()))
            group_labels = config_group_mapper(list(group_measurements.keys()))
            data = list(group_measurements.values())
            
            stat_signif = MannWhitneyUCliffDelta({group : value for group, value in zip(group_labels, group_measurements.values())})
            pprint.pprint(stat_signif.p_values)
            pprint.pprint(stat_signif.effect_size)
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes     
            boxplot = axi.boxplot(data, tick_labels=group_labels, patch_artist=True)
            axi.set_title(self.vessel_num_labels[i])
            axi.set_ylabel('Risk distance')
            axi.set_aspect('auto', adjustable='box')
            axi.set_xticklabels(group_labels, rotation=45, ha='right')
            # Set colors and border widths for each box
            for patch, color in zip(boxplot['boxes'], group_colors):
                patch.set_facecolor(color)           # Set fill color
                patch.set_linewidth(1.5)               # Set border width
            
            for element in ['whiskers', 'caps', 'medians']:
                for comp in boxplot[element]:
                    if element == 'medians':
                        comp.set_color('red')
                    comp.set_linewidth(1.5)
            
            
            # Annotate each box with the number of samples
            for i, group in enumerate(data, 1):  # '1' because boxplot groups start at 1
                sample_size = len(group)
                axi.text(i, 1.1, f'{sample_size}', ha='center', va='center', fontsize=12, horizontalalignment='center')

            axi.set_ylim(0, 1.2)

        fig.tight_layout()