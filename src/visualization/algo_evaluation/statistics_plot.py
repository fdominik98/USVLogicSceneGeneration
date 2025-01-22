from collections import defaultdict
import pprint
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot

class StatisticsPlot(MyPlot):  
    def __init__(self, eval_datas : List[EvaluationData]): 
        self.eval_datas = eval_datas
        self.measurements : Dict[int, List[FunctionalScenario]] = defaultdict(lambda : [])
        for eval_data in eval_datas:
            if eval_data.best_fitness_index == 0:    
                self.measurements[eval_data.vessel_number].append(eval_data)  
                
        self.vessel_num_labels = vessel_number_mapper(list(self.measurements.keys()))       
        MyPlot.__init__(self)
        
    def create_fig(self):
        fig, axes = plt.subplots(1, 2, figsize=(1 * 3, 4))
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)
        
        fig.text(0.5, 0.5, 'MSR', ha='center', va='center', fontsize=12, fontweight='bold')
        fig.text(0.5, 0.05, 'SBO', ha='center', va='center', fontsize=12, fontweight='bold')

        for i, (vessel_num, eval_datas) in enumerate(self.measurements.items()):
            functional_models = [ConcreteSceneAbstractor.get_abstractions_from_eval(eval_data).functional_scenario for eval_data in eval_datas]
            colors = group_colors(3)
            labels = ['Head-on', 'Crossing', 'Overtaking']
            values = [sum(len(model.head_on_interpretation)/2 for model in functional_models), 
                      sum(len(model.crossing_interpretation) for model in functional_models),
                      sum(len(model.overtaking_interpretation) for model in functional_models)]
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes  
            bars : plt.BarContainer = axi.bar(labels, values, color=colors[i], edgecolor='black', linewidth=0)
            if i == 0:
                axi.set_title(self.vessel_num_labels[i])
                axi.set_ylabel('Samples')
            axi.set_aspect('auto', adjustable='box')
            yticks = np.linspace(0, max(values), 6)
            yticks = [int(t) for t in yticks] 
            axi.set_yticks([yticks[0], yticks[-1]] + list(yticks), minor=False) 

        fig.tight_layout(rect=[0, 0.04, 1, 1])