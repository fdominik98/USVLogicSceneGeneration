from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, List, Tuple
from matplotlib import pyplot as plt
import numpy as np
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from utils.evaluation_config import SB, MSR_SB, RS, MSR_RS, CD_RS, TS_RS

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
    config_group_map = {SB : 'Base-SB',
                        MSR_SB : 'MSR-SB',
                        RS : 'Base-RS',
                        TS_RS : 'Base-RS+',
                        CD_RS : 'MSR-RS',                        
                        MSR_RS : 'MSR-RS+',
                        'common_ocean_benchmark' : 'CO',
                        'zhu_et_al' : 'Zhu',
                        'base_reference' : 'BaseRef'}
    
    colors = {
        SB : np.array([0.698, 0.875, 0.541, 1]),
        RS : np.array([0.792, 0.698, 0.839, 1]),
        MSR_SB : np.array([0.122, 0.471, 0.705, 1]),
        MSR_RS : np.array([0.902, 0.333, 0.051, 1]),
        CD_RS : np.array([0.494, 0.282, 0.415, 1]),            
        TS_RS : np.array([0.361, 0.596, 0.643, 1]),
    }
                
    
    actor_numbers_by_type_map = {
        (2, 0) : '2 vessels', (2, 1) : '2 vessels, 1 obstacle', (3, 0) : '3 vessels', (3, 1) : '3 vessels, 1 obstacle', (4, 0) : '4 vessels', (5, 0) : '5 vessels', (6, 0) : '6 vessels', 
    }
    
    algo_map = {'nsga2' : 'N2', 'nsga3' : 'N3', 'ga' : 'GA', 'de' : 'DE', 'pso' : 'PSO', 'scenic' : 'Scenic'}
    aggregate_map = {'all' : r'$\sum{}$', 'actor' : 'A', 'category' : 'C', 'all_swarm' : r'$\sum{s}$'}
       
    def __init__(self, eval_datas : List[EvaluationData], is_algo=False, is_all=False) -> None:
        self.comparison_groups : List[Any] = self.algos if is_algo else self.config_groups
        self.comparison_group_count = len(self.comparison_groups)
        self.vessel_num_count = len(self.actor_numbers_by_type)
        # self.colors = self.generate_colors(self.comparison_group_count)
        self.markers = ['o', 's', '^', 'D', 'v', 'x', '*', 'P', 'h']
        self.vessel_num_labels = [self.actor_numbers_by_type_map[vn] for vn in self.actor_numbers_by_type]
        self.group_labels = [self.algo_map[algo] + '-' + self.aggregate_map[aggregate] for algo, aggregate in self.algos] if is_algo else [self.config_group_map[cg.lower()] for cg in self.config_groups]
        
        self.measurements : Dict[Tuple[int, int], Dict[str, Dict[int, List[EvaluationData]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        # for actor_number_by_type in self.actor_numbers_by_type:
        #     for comparison_group in self.comparison_groups:
        #         self.measurements[actor_number_by_type][comparison_group] = []   
        
        self.eval_datas : List[EvaluationData] = sorted(eval_datas, key=lambda eval_data: eval_data.timestamp)
        for eval_data in self.eval_datas:
            comparison_group = (eval_data.algorithm_desc.lower(), eval_data.aggregate_strat.lower()) if is_algo else eval_data.config_group.lower()    
            if (not is_all and not eval_data.is_valid) or comparison_group not in self.comparison_groups or eval_data.actor_number_by_type not in self.actor_numbers_by_type:
                continue
            self.measurements[eval_data.actor_number_by_type][comparison_group][eval_data.random_seed].append(eval_data) 
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
        #return [np.array([color[0], color[1], color[2], 0.7]) for color in colors]
        return [np.array([0.698, 0.875, 0.541, 1]),
                np.array([0.792, 0.698, 0.839, 1]), 
                np.array([0.122, 0.471, 0.705, 1]),
                np.array([0.902, 0.333, 0.051, 1]),
                np.array([0.361, 0.596, 0.643, 1]),  # darker teal-blue
                np.array([0.494, 0.282, 0.415, 1])]  # muted plum/purple
    
    def set_yticks(self, axi : plt.Axes, values, unit : str = None, tick_number : int = 6):
        if values is None or len(values) == 0:
            return
        yticks = np.linspace(0, max(values), tick_number)
        yticks = [round(t) for t in yticks] 
        if unit is None:
            ytick_labels = yticks
        else:
            ytick_labels = [f'{round(t)}{unit}' for t in yticks] 
        axi.set_yticks([yticks[0], yticks[-1]] + list(yticks), minor=False)
        axi.set_yticklabels([ytick_labels[0], ytick_labels[-1]] + list(ytick_labels))
        
    def set_xticks(self, axi : plt.Axes, values, unit : str = None, tick_number : int = 6, rotation: int = 45):
        xticks = np.linspace(0, max(values), tick_number)
        xticks = [round(t) for t in xticks] 
        if unit is None:
            xtick_labels = xticks
        else:
            xtick_labels = [f'{round(t)}{unit}' for t in xticks] 
        axi.set_xticks([xticks[0], xticks[-1]] + list(xticks), minor=False)
        axi.set_xticklabels([xtick_labels[0], xtick_labels[-1]] + list(xtick_labels), rotation=rotation)
        
    def init_axi(self, pos : int, axi : plt.Axes, label : str):
        axi.set_aspect('auto', adjustable='box')
        if pos == 0:
            axi.set_ylabel(label, fontsize=14)
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
        return [SB, MSR_SB, RS, MSR_RS, 'common_ocean_benchmark']
    
    @property
    def actor_numbers_by_type(self) -> List[Tuple[int, int]]:
        return [(2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (5, 0), (6, 0)]