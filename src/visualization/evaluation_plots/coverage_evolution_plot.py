from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from visualization.plotting_utils import EvalPlot

class CoverageEvolutionPlot(EvalPlot):  
    def __init__(self, eval_datas : List[EvaluationData], get_equivalence_class_distribution=ConcreteSceneAbstractor.get_equivalence_class_distribution): 
        self.get_equivalence_class_distribution = get_equivalence_class_distribution
        super().__init__(eval_datas, is_all=True)
        
    @property   
    def config_groups(self) -> List[str]:
        return ['sb-o', 'sb-msr', 'rs-o', 'rs-msr']
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        return [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
        
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(self.comparison_group_count, self.vessel_num_count, figsize=(3 * 4, 3.8), constrained_layout=True)
        axes = np.atleast_2d(axes)
        
        for i, actor_number_by_type in enumerate(self.actor_numbers_by_type):
            for j, config_group in enumerate(self.comparison_groups):
                axi : plt.Axes = axes[j][i]
                if j == 0:
                    axi.set_title(self.vessel_num_labels[i])                    
                self.init_axi(i, axi, r"$\bf{" + self.group_labels[j] + r"}$" + "\nCoverage (%)")
                
                values : List[float] = [0]
                equivalence_classes : Dict[int, Tuple[FunctionalScenario, int]] = {}
                for eval_data in self.measurements[actor_number_by_type][config_group]:
                    if eval_data.is_valid:
                        new_classes = self.get_equivalence_class_distribution([eval_data.best_scene], actor_number_by_type)
                        for key, value in new_classes.items():
                            if key in equivalence_classes:
                                equivalence_classes[key] = (value[0], equivalence_classes[key][1] + value[1])
                            else:
                                equivalence_classes[key] = value
                    
                        covered_classes = sum(1 for _, count in equivalence_classes.values() if count > 0)
                        values.append(covered_classes / len(new_classes) * 100 if len(new_classes) != 0 else 0)
                    else:
                        values.append(values[-1])
                
                if len(values) == 1:
                    continue
                        
                labels = list(range(len(values)))
                axi.plot(labels, values, color=self.colors[j], linestyle='-', linewidth=5)
                
                xticks = list(np.linspace(labels[0], labels[-1], 6))
                xticks = [int(t) for t in xticks] 
                axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False) 
                self.set_yticks(axi, values)
                
        return fig
        
class AmbiguousCoverageEvolutionPlot(CoverageEvolutionPlot):
    def __init__(self, eval_datas):
        super().__init__(eval_datas, ConcreteSceneAbstractor.get_ambiguous_equivalence_class_distribution)
        