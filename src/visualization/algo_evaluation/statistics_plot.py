from typing import List
import matplotlib.pyplot as plt
import numpy as np
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from evaluation.vessel_type_sampler import VesselTypeSampler
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from visualization.plotting_utils import EvalPlot

class StatisticsPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData]):                
        self.sample_size = 4000
        self.distribution = {'OtherType' : 51.1, 'CargoShip' : 31.1,
                            'Tanker' : 6.2, 'ContainerShip' : 7.4,
                            'PassengerShip' : 0.7, 'FishingShip' : 3.5}
        super().__init__(eval_datas)
        
    @property   
    def config_groups(self) -> List[str]:
        return ['SBO', 'scenic_distribution', 'common_ocean_benchmark', 'zhu_et_al']
    
    @property
    def vessel_numbers(self) -> List[int]:
        return [2]
        
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(self.vessel_num_count, self.group_count, figsize=(1 * 12, 4))
        axes = np.atleast_1d(axes)
        
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
        for i, vessel_number in enumerate(self.vessel_numbers):
            for j, config_group in enumerate(self.config_groups):
                scenarios = [ConcreteSceneAbstractor.get_abstractions_from_eval(eval_data) for eval_data in self.measurements[vessel_number][config_group]]
                values = VesselTypeSampler.sample(scenarios, self.sample_size, {})
                if sum(values) == 0:
                    continue
                configure_axi(j, self.group_labels[j], self.colors[j], values)
            
        configure_axi(3, self.group_labels[3], self.colors[3], [56952*0.131, 56952*0.002, 56952*0.867])
            
        fig.tight_layout(rect=[0, 0.04, 1, 1])
        return fig