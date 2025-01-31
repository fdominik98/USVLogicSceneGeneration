from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Tuple
from matplotlib import pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData

class PlotBase(ABC):
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['font.size'] = 12
    
    def __init__(self):
        super().__init__()
        self.fig = self.create_fig()
    
    @abstractmethod
    def create_fig(self) -> plt.Figure:
        pass

class EvalPlot(PlotBase, ABC):    
    config_group_map = {'sbo' : 'SBO',
                        'msr' : 'MSR',
                        'scenic_distribution' : 'Scenic',
                        'common_ocean_benchmark' : 'Common',
                        'zhu_et_al' : 'Zhu et al.'}
    
    vessel_number_map = {
        2 : '2 Vessels', 3 : '3 Vessels', 4 : '4 Vessels', 5 : '5 Vessels', 6 : '6 Vessels', 
    }
    
    algo_map = {'nsga2' : 'N2', 'nsga3' : 'N3', 'ga' : 'GA', 'de' : 'DE', 'pso' : 'PSO'}
    aggregate_map = {'all' : 'A', 'vessel' : 'V', 'category' : 'C', 'all_swarm' : 'A'}
       
    def __init__(self, eval_datas : List[EvaluationData], algo=False, all=False) -> None:
        self.group_count = len(self.config_groups)
        self.vessel_num_count = len(self.vessel_numbers)
        self.algo_count = len(self.algos)
        self.colors = self.generate_colors(self.group_count)
        self.algo_colors = self.generate_colors(self.algo_count)
        self.vessel_num_labels = [self.vessel_number_map[vn] for vn in self.vessel_numbers]
        self.group_labels = [self.config_group_map[cg.lower()] for cg in self.config_groups]
        self.algo_labels = [self.algo_map[algo] + '-' + self.aggregate_map[aggregate] for algo, aggregate in self.algos]
        
        self.measurements : Dict[int, Dict[str, List[EvaluationData]]] = defaultdict(lambda: defaultdict(list))
        for vessel_number in self.vessel_numbers:
            for config_group in self.config_groups:
                self.measurements[vessel_number][config_group] = []   
        
        self.eval_datas = eval_datas
        if not algo:        
            for eval_data in eval_datas:
                if (eval_data.best_fitness_index != 0 and not all) or eval_data.config_group not in self.config_groups or eval_data.vessel_number not in self.vessel_numbers:
                    continue
                self.measurements[eval_data.vessel_number][eval_data.config_group].append(eval_data) 
        else:
            for eval_data in eval_datas:
                if (eval_data.best_fitness_index != 0 and not all) or eval_data.algorithm_desc not in self.algos or eval_data.vessel_number not in self.vessel_numbers:
                    continue
                self.measurements[eval_data.vessel_number][eval_data.algorithm_desc].append(eval_data)             
        super().__init__()                
        
    
    @property   
    @abstractmethod
    def config_groups(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def vessel_numbers(self) -> List[int]:
        pass
    
    @property
    def algos(self) -> List[Tuple[str, str]]:
        return []
    
    def generate_colors(self, size) -> List[np.ndarray]:
        # Convert the colors to RGB format
        color1_rgb = np.array((0, 0.5, 1))
        # if size == 1:
        #     return color1_rgb
        color2_rgb = np.array((1, 0.5, 0))
        # Generate a range of colors by linear interpolation
        colors = [color1_rgb + (color2_rgb - color1_rgb) * i / (size - 1) for i in range(size)]
        return [np.array([color[0], color[1], color[2], 0.7]) for color in colors]
    
class DummyEvalPlot(EvalPlot):
    def __init__(self, eval_datas):
        super().__init__(eval_datas)
    
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(1, 1, figsize=(7, 7))
        self.axi : plt.Axes = axes
        return fig
        
    @property   
    def config_groups(self) -> List[str]:
        return ['SBO', 'scenic_distribution', 'common_ocean_benchmark']
    
    @property
    def vessel_numbers(self) -> List[int]:
        return [2, 3, 4, 5, 6]