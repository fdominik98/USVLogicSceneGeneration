from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, List, Tuple
from matplotlib import pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData

class PlotBase(ABC):
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['font.size'] = 12
    plt.rcParams['pdf.fonttype'] = 42
    
    def __init__(self):
        super().__init__()
        self.fig = self.create_fig()
    
    @abstractmethod
    def create_fig(self) -> plt.Figure:
        pass

class EvalPlot(PlotBase, ABC):    
    config_group_map = {'sb-o' : 'SB-O',
                        'sb-msr' : 'SB-MSR',
                        'rs-o' : 'RS-O',
                        'rs-msr' : 'RS-MSR',
                        'common_ocean_benchmark' : 'CO',
                        'zhu_et_al' : 'Zhu',
                        'base_reference' : 'BaseRef'}
    
    actor_numbers_by_type_map = {
        (2, 0) : '2 vessels', (2, 1) : '2 vessels, 1 obstacle', (3, 0) : '3 vessels', (3, 1) : '3 vessels, 1 obstacle', (4, 0) : '4 vessels', (5, 0) : '5 vessels', (6, 0) : '6 vessels', 
    }
    
    algo_map = {'nsga2' : 'N2', 'nsga3' : 'N3', 'ga' : 'GA', 'de' : 'DE', 'pso' : 'PSO', 'scenic' : 'Scenic'}
    aggregate_map = {'all' : r'$\sum{}$', 'actor' : 'A', 'category' : 'C', 'all_swarm' : r'$\sum{s}$'}
       
    def __init__(self, eval_datas : List[EvaluationData], is_algo=False, is_all=False) -> None:
        self.comparison_groups : List[Any] = self.algos if is_algo else self.config_groups
        self.comparison_group_count = len(self.comparison_groups)
        self.vessel_num_count = len(self.actor_numbers_by_type)
        self.colors = self.generate_colors(self.comparison_group_count)
        self.vessel_num_labels = [self.actor_numbers_by_type_map[vn] for vn in self.actor_numbers_by_type]
        self.group_labels = [self.algo_map[algo] + '-' + self.aggregate_map[aggregate] for algo, aggregate in self.algos] if is_algo else [self.config_group_map[cg.lower()] for cg in self.config_groups]
        
        self.measurements : Dict[Tuple[int, int], Dict[str, List[EvaluationData]]] = defaultdict(lambda: defaultdict(list))
        for actor_number_by_type in self.actor_numbers_by_type:
            for comparison_group in self.comparison_groups:
                self.measurements[actor_number_by_type][comparison_group] = []   
        
        self.eval_datas : List[EvaluationData] = sorted(eval_datas, key=lambda eval_data: eval_data.timestamp)
        for eval_data in self.eval_datas:
            comparison_group = (eval_data.algorithm_desc.lower(), eval_data.aggregate_strat.lower()) if is_algo else eval_data.config_group.lower()    
            if (not is_all and not eval_data.is_valid) or comparison_group not in self.comparison_groups or eval_data.actor_number_by_type not in self.actor_numbers_by_type:
                continue
            self.measurements[eval_data.actor_number_by_type][comparison_group].append(eval_data) 
        super().__init__()                
        
    
    @property   
    @abstractmethod
    def config_groups(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
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
    
    def set_yticks(self, axi : plt.Axes, values):
        yticks = np.linspace(0, max(values), 6)
        yticks = [round(t) for t in yticks] 
        axi.set_yticks([yticks[0], yticks[-1]] + list(yticks), minor=False)
        
    def init_axi(self, pos : int, axi : plt.Axes, label : str):
        axi.set_aspect('auto', adjustable='box')
        if pos == 0:
            axi.set_ylabel(label)
        axi.set_yticks([])
        axi.set_xticks([])
    
class DummyEvalPlot(EvalPlot):
    def __init__(self, eval_datas):
        super().__init__(eval_datas)
    
    def create_fig(self) -> plt.Figure:
        fig, axes = plt.subplots(1, 1, figsize=(7, 7))
        self.axi : plt.Axes = axes
        return fig
        
    @property   
    def config_groups(self) -> List[str]:
        return ['sb-o', 'sb-msr', 'rs-o', 'rs-msr', 'common_ocean_benchmark']
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        return [(2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (5, 0), (6, 0)]