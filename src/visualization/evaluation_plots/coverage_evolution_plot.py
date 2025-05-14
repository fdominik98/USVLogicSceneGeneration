from typing import Dict, List, Tuple
from matplotlib import gridspec
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
        fig = plt.figure(figsize=(3 * self.vessel_num_count, 1.5 * 2), constrained_layout=True)
        gs = gridspec.GridSpec(2, self.vessel_num_count, height_ratios=[1,1]) 
        # Top axes spans all 6 columns
        ax_top = [fig.add_subplot(gs[0, i]) for i in range(self.vessel_num_count)] 
        # Bottom row: 6 equal-width axes
        ax_bottom = [fig.add_subplot(gs[1, i]) for i in range(self.vessel_num_count)] 
        axes = [ax_top, ax_bottom]
        
        for i, actor_number_by_type in enumerate(self.actor_numbers_by_type):
            max_value = 0
            values : Dict[str, List[int]] = dict()
            relevant_values : Dict[str, List[int]] = dict()
            ambiguous_values : Dict[str, List[int]] = dict()
            for config_group in self.comparison_groups:
                values[config_group] = [0]
                relevant_values[config_group] = [0]
                ambiguous_values[config_group] = [0]
                equivalence_classes : Dict[int, Tuple[ConcreteScene, int]] = {}
                for eval_data in self.measurements[actor_number_by_type][config_group]:
                    if eval_data.is_valid:
                        new_classes = ConcreteSceneAbstractor.get_equivalence_class_distribution([eval_data.best_scene], self.is_second_level_abstraction)
                        for key, value in new_classes.items():
                            if key in equivalence_classes:
                                equivalence_classes[key] = (value[0], equivalence_classes[key][1] + value[1])
                            else:
                                equivalence_classes[key] = value
                        values[config_group].append(len(equivalence_classes))
                        relevant_values[config_group].append(sum(1 for scene, count in equivalence_classes.values() if scene.is_relevant))
                        ambiguous_values[config_group].append(sum(1 for scene, count in equivalence_classes.values() if scene.is_ambiguous))
                    else:
                        values[config_group].append(values[config_group][-1])
                        relevant_values[config_group].append(relevant_values[config_group][-1])
                        ambiguous_values[config_group].append(ambiguous_values[config_group][-1])
            for k in range(2): 
                axi : plt.Axes = axes[k][i]
                if k == 0:
                    axi.set_title(self.vessel_num_labels[i], fontweight='bold')   
                    row_label = "Covered " + r"$\bf{relevant}$" +"\nequivalence classes" 
                    values_to_plot = relevant_values
                else:
                    row_label = "Covered " + r"$\bf{ambiguous}$" +"\nequivalence classes"        
                    values_to_plot = ambiguous_values  
                #self.init_axi(i, axi, r"$\bf{" + self.group_labels[j] + r"}$" + "\nCovered classes")
                self.init_axi(i, axi, row_label)
                
                max_length = max(len(lst) for lst in values.values())
                if max_length == 1:
                    continue            
                        
                labels = list(range(max_length))
                
                for j, config_group in enumerate(self.comparison_groups):
                    axi.plot(labels, values_to_plot[config_group], color=self.colors[j], linestyle='-', linewidth=3.5, label=r"$\bf{" + self.group_labels[j] + r"}$")
                
                max_value = max(i for lst in list(relevant_values.values()) + list(ambiguous_values.values()) for i in lst)
                higher_max = round(max_value + max(max_value * 0.1, 1))
                self.set_yticks(axi, range(higher_max + 1))
                axi.set_ylim(0, higher_max)
                
                if k==1:
                    xticks = list(np.linspace(labels[0], labels[-1], 6))
                    xticks = [int(t) for t in xticks] 
                    axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False) 
                
        # Get handles and labels from the last axis (or any axis — all are the same here)
        handles, labels = axes[1][0].get_legend_handles_labels()
        # Add one legend to the figure (outside bottom)
        axes[1][0].legend(handles, labels, ncol=1, fontsize=10, title="Approaches")
        return fig
        