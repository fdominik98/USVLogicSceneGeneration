from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from concrete_level.models.concrete_scene import ConcreteScene
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from visualization.plotting_utils import EvalPlot

class DiversityPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], is_second_level_abstraction=False, is_relevant=True): 
        self.is_second_level_abstraction = is_second_level_abstraction
        self.is_relevant = is_relevant
        super().__init__(eval_datas)
        
    
    @property   
    def config_groups(self) -> List[str]:
        #return ['sb-o', 'rs-o', 'sb-msr', 'rs-msr', 'common_ocean_benchmark']
        return ['sb-o', 'rs-o', 'sb-msr', 'rs-msr']
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        #return [(2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (5, 0), (6, 0)]
        return [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
        
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(self.comparison_group_count, self.vessel_num_count, figsize=(2.5 * 4, 3.8), constrained_layout=True,
                                 gridspec_kw={'wspace': 0, 'hspace': 0})
        axes = np.atleast_2d(axes)
        
        for i, actor_number_by_type in enumerate(self.actor_numbers_by_type):
            max_value = 0
            all_axes : List[plt.Axes] = []
            for j, config_group in enumerate(self.comparison_groups):
                axi : plt.Axes = axes[j][i]
                all_axes.append(axi)
                if j == 0:
                    axi.set_title(self.vessel_num_labels[i], fontweight='bold')                    
                self.init_axi(i, axi, r"$\bf{" + self.group_labels[j] + r"}$")
                
                equivalence_classes : Dict[int, Tuple[ConcreteScene, int]] = ConcreteSceneAbstractor.get_equivalence_class_distribution(
                    [eval_data.best_scene for eval_data in self.measurements[actor_number_by_type][config_group]],
                    self.is_second_level_abstraction)
                
                if self.is_relevant:
                    equivalence_classes = {key : (scene, count) for key, (scene, count) in equivalence_classes.items() if scene.is_relevant_by_fec}
                else :
                    equivalence_classes = {key : (scene, count) for key, (scene, count) in equivalence_classes.items()}
                equivalence_classes = dict(sorted(equivalence_classes.items(), key=lambda item: item[1][1], reverse=True))
                values = [int(count) for _, count in equivalence_classes.values()]
                    
                all_shapes = len(equivalence_classes)
                relevant_shapes = sum(1 for scene, count in equivalence_classes.values() if scene.is_relevant_by_fec)
                ambiguous_shapes = sum(1 for scene, count in equivalence_classes.values() if scene.is_ambiguous_by_fec)
                
                #plot_text = f'all shapes: {all_shapes}\nrelevant shapes: {relevant_shapes}\nambiguous shapes: {ambiguous_shapes}'
                # plot_text = f'covered: {all_shapes}'
                
                # axi.text(0.98, 0.98, plot_text, 
                # transform=axi.transAxes,  # Use axis coordinates
                # verticalalignment='top', # Align text vertically to the top
                # horizontalalignment='right',
                # fontsize=11)
                
                if sum(values) == 0:
                    continue
                if max_value < max(values):
                    max_value = max(values)
                
                labels = range(1, len(equivalence_classes.keys()) + 1)
                bars : plt.BarContainer = axi.bar(labels, values, color=self.colors[j], edgecolor='black', linewidth=0)
                
                xticks = list(np.linspace(labels[0], labels[-1], 2))
                xticks = [int(t) for t in xticks] 
                axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False) 
                # axi.set_xticks([1], minor=False) 
                # axi.set_xticklabels([f'all shapes: {all_shapes}'], minor=False)
                
                higher_max = round(max(values) * 1.1) + 1
                self.set_yticks(axi, range(higher_max), tick_number=2)
                axi.set_ylim(0, higher_max)
            # for ax in all_axes:
            #     self.set_yticks(ax, range(max_value + 1), tick_number=2)
            #     ax.set_ylim(0, max_value)
                
        return fig

        
class AmbiguousDiversityPlot(DiversityPlot):
    def __init__(self, eval_datas, is_higher_abstraction=False):
        super().__init__(eval_datas, is_higher_abstraction)
        
