from collections import defaultdict
import pprint
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from evaluation.vessel_type_sampler import VesselTypeSampler
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
                self.measurements[eval_data.config_group].append(eval_data)  
                
        self.sample_size = 4000
        self.colors = group_colors(4)
        self.distribution = {'OtherType' : 51.1, 'CargoShip' : 31.1,
                            'Tanker' : 6.2, 'ContainerShip' : 7.4,
                            'PassengerShip' : 0.7, 'FishingShip' : 3.5}

        MyPlot.__init__(self)
        
    def create_fig(self):
        fig, axes = plt.subplots(1, 4, figsize=(1 * 12, 4))
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        
        def configure_axi(i : int, group_label, color, values):
            axi : plt.Axes = axes[i]
            bars : plt.BarContainer = axi.bar(labels, values, color=color, edgecolor='black', linewidth=0)
            axi.set_title(group_label)
            if i == 0:
                axi.set_ylabel('Samples')
            axi.set_aspect('auto', adjustable='box')
            yticks = np.linspace(0, max(values)*1.1, 6)
            yticks = [int(t) for t in yticks] 
            axi.set_yticks([yticks[0], yticks[-1]] + list(yticks), minor=False) 
            
            for i, bar in enumerate(bars):
                axi.text(bar.get_x() + bar.get_width() / 2, values[i] * 1.02, 
                f'{(values[i] / sum(values) * 100):.1f}%', ha='center', va='bottom', fontsize=10)


        labels = ['Overtaking', 'Head-on', 'Crossing']
        for i, (config_group, eval_datas) in enumerate(self.measurements.items()):
            group_label = config_group_mapper([config_group])
            scenarios = [ConcreteSceneAbstractor.get_abstractions_from_eval(eval_data) for eval_data in eval_datas]
            values = VesselTypeSampler.sample(scenarios, self.sample_size, {})
            configure_axi(i, group_label[0], self.colors[i], values)
            
        configure_axi(3, 'Zhu et al.', self.colors[-1], [56952*0.131, 56952*0.002, 56952*0.867])
            
        fig.tight_layout(rect=[0, 0.04, 1, 1])