from typing import List
import matplotlib.pyplot as plt
import numpy as np
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from evaluation.vessel_type_sampler import VesselTypeSampler
from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from visualization.plotting_utils import EvalPlot

class ScenarioTypeStatisticsPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData]):                
        self.sample_size = 4000
        self.distribution = {'OtherType' : 51.1, 'CargoShip' : 31.1,
                            'Tanker' : 6.2, 'ContainerShip' : 7.4,
                            'PassengerShip' : 0.7, 'FishingShip' : 3.5}
        
        self.labels = ['Overtake', 'Head-on', 'Crossing']
        super().__init__(eval_datas)
        
    @property   
    def config_groups(self) -> List[str]:
        return ['SBO', 'scenic_distribution', 'common_ocean_benchmark', 'zhu_et_al', 'base_reference']
    
    @property
    def vessel_numbers(self) -> List[int]:
        return [2, 3, 4, 5, 6]
        
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(self.vessel_num_count, self.comparison_group_count, figsize=(1 * 14, 2*self.vessel_num_count), constrained_layout=True)
        axes = np.atleast_2d(axes)
        
        def configure_axi(i : int, j : int, group_label, color, values):
            axi : plt.Axes = axes[i][j]
            self.init_axi(j, axi, f'{self.vessel_numbers[i]}-vessel samples')
            if sum(values) == 0:
                return
            
            bars : plt.BarContainer = axi.bar(self.labels, values, color=color, edgecolor='black', linewidth=0)
            axi.set_title(group_label, fontdict={'fontsize': 12, 'fontweight': 'bold'})
            self.set_yticks(axi, values)
            axi.set_xticks([0,1,2], self.labels)
            axi.set_xticklabels(self.labels, rotation=0, ha='center')  
            
            axi.set_ylim(0, max(values) * 1.15)
            
            for i, bar in enumerate(bars):
                axi.text(bar.get_x() + bar.get_width() / 2, values[i] * 1.02, 
                f'{(values[i] / sum(values) * 100):.1f}%', ha='center', va='bottom', fontsize=10)
                
                
            axi.text(0.5, 0.92, f'total: {int(sum(values))}', 
                transform=axi.transAxes,  # Use axis coordinates
                verticalalignment='top', # Align text vertically to the top
                horizontalalignment='center',
                fontsize=11,
                fontweight='bold')


        for i, vessel_number in enumerate(self.vessel_numbers):
            for j, comparison_group in enumerate(self.comparison_groups):
                scenarios = [ConcreteSceneAbstractor.get_abstractions_from_eval(eval_data).functional_scenario for eval_data in self.measurements[vessel_number][comparison_group]]
                values = VesselTypeSampler.sample(scenarios, self.sample_size, {})
                configure_axi(i, j, self.group_labels[j], self.colors[j], values)
            
            if self.vessel_numbers[i] == 2:
                configure_axi(i, 3, self.group_labels[3], self.colors[3], [56952*0.131, 56952*0.002, 56952*0.867])
            configure_axi(i, 4, self.group_labels[4], self.colors[4],
                          VesselTypeSampler.sample(FunctionalModelManager.get_x_vessel_scenarios(vessel_number), self.sample_size, {}))
        
        return fig