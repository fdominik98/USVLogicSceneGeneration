from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from concrete_level.models.concrete_scene import ConcreteScene
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from visualization.plotting_utils import EvalPlot

class CoverageEvolutionPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], is_second_level_abstraction = False): 
        self.is_second_level_abstraction = is_second_level_abstraction
        super().__init__(eval_datas, is_all=True)
        
    @property   
    def config_groups(self) -> List[str]:
        #return ['sb-o', 'rs-o', 'sb-msr', 'rs-msr', 'common_ocean_benchmark']
        return ['sb-o', 'rs-o', 'sb-msr', 'rs-msr']
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        #return [(2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (5, 0), (6, 0)]
        return [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
        
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(self.comparison_group_count, self.vessel_num_count, figsize=(3 * 4, 3.8), constrained_layout=True)
        axes = np.atleast_2d(axes)
        
        for i, actor_number_by_type in enumerate(self.actor_numbers_by_type):
            max_value = 0
            all_axes : List[plt.Axes] = []
            for j, config_group in enumerate(self.comparison_groups):
                axi : plt.Axes = axes[j][i]
                all_axes.append(axi)
                if j == 0:
                    axi.set_title(self.vessel_num_labels[i])                    
                self.init_axi(i, axi, r"$\bf{" + self.group_labels[j] + r"}$" + "\nCovered classes")
                
                values : List[int] = [0]
                relevant_values : List[int] = [0]
                ambiguous_values : List[int] = [0]
                equivalence_classes : Dict[int, Tuple[ConcreteScene, int]] = {}
                for eval_data in self.measurements[actor_number_by_type][config_group]:
                    if eval_data.is_valid:
                        new_classes = ConcreteSceneAbstractor.get_equivalence_class_distribution([eval_data.best_scene], self.is_second_level_abstraction)
                        for key, value in new_classes.items():
                            if key in equivalence_classes:
                                equivalence_classes[key] = (value[0], equivalence_classes[key][1] + value[1])
                            else:
                                equivalence_classes[key] = value
                        values.append(len(equivalence_classes))
                        relevant_values.append(sum(1 for scene, count in equivalence_classes.values() if scene.is_relevant))
                        ambiguous_values.append(sum(1 for scene, count in equivalence_classes.values() if scene.is_ambiguous))
                    else:
                        values.append(values[-1])
                        relevant_values.append(relevant_values[-1])
                        ambiguous_values.append(ambiguous_values[-1])
                
                if len(values) == 1:
                    continue
                
                if max_value < max(values):
                    max_value = max(values)
                        
                labels = list(range(len(values)))
                axi.plot(labels, values, color=self.colors[j], linestyle='-', linewidth=6)
                axi.plot(list(range(len(relevant_values))), relevant_values, color='blue', linestyle='-', linewidth=1.5)
                axi.plot(list(range(len(ambiguous_values))), ambiguous_values, color='red', linestyle='-', linewidth=1.5)
                
                xticks = list(np.linspace(labels[0], labels[-1], 6))
                xticks = [int(t) for t in xticks] 
                axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False) 
            
            for ax in all_axes:
                self.set_yticks(ax, range(max_value + 1))
                ax.set_ylim(0, max_value)
                
        return fig
        