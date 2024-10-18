from collections import defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from evaluation.eqv_class_calculator import EqvClassCalculator
from model.environment.functional_models import MSR
from model.relation import RelationDescClause
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, config_group_mapper, vessel_number_mapper, group_colors
from visualization.my_plot import MyPlot

equiv_classes : dict[int, List[RelationDescClause]] = {
    3 :  [inter.relation_desc_clauses[0] for inter in MSR.three_vessel_interactions],
    4 :  [inter.relation_desc_clauses[0] for inter in MSR.four_vessel_interactions],
    5 :  [inter.relation_desc_clauses[0] for inter in MSR.five_vessel_interactions],
    6 :  [inter.relation_desc_clauses[0] for inter in MSR.six_vessel_interactions]
}

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
                found_length = len(data)
                for equiv_class in equiv_classes[vessel_num]:
                    ass_clause = equiv_class.get_asymmetric_clause()
                    ass_clause.remove_non_ego_ralations()
                    if ass_clause not in data:
                        data[ass_clause] = 0
                data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
                labels = range(1, len(data.keys()) + 1)
                values = [int(v) for v in data.values()]
                
                if isinstance(axes, np.ndarray):
                    axi : plt.Axes = axes[j][i]
                else:
                    axi : plt.Axes = axes  
                bars : plt.BarContainer = axi.bar(labels, values, color=group_colors(len(group_labels)), edgecolor='black', linewidth=0)
                axi.set_title(self.vessel_num_labels[i])
                axi.set_ylabel('Samples')
                axi.set_aspect('auto', adjustable='box')
                yticks = np.linspace(0, max(values), 6)
                yticks = [int(t) for t in yticks] 
                axi.set_yticks([yticks[0], yticks[-1]] + list(yticks), minor=False) 
                xticks = np.linspace(labels[0], labels[-1], 6)
                xticks = [int(t) for t in xticks] 
                axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False)             
            
                axi.text(0.98, 0.98, f'covered shapes: {found_length}/{len(data)}', 
                transform=axi.transAxes,  # Use axis coordinates
                verticalalignment='top', # Align text vertically to the top
                horizontalalignment='right',
                fontsize=10)

        fig.tight_layout()