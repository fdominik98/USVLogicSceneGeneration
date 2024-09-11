from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from matplotlib import pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from trajectory_planning.proximity_evaluator import DynamicMetrics
from visualization.plot_component import PlotComponent, colors
import matplotlib.colors as mcolors

class AxesComponent(PlotComponent, ABC):
    def __init__(self, ax : plt.Axes, initial_visibility : bool, env : USVEnvironment, metrics : List[DynamicMetrics]) -> None:
        super().__init__(ax, initial_visibility, env)
        self.metrics = metrics
        self.line_graphs : Dict[str, plt.Line2D] = {}
        self.ax = ax
        
        self.ax.set_title(f'{self.get_metric_str()} over time')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel(f'{self.get_metric_str()} (m)')
        self.ax.set_aspect('equal', adjustable='box')      
    
    @abstractmethod
    def get_y_metric(self, metric : DynamicMetrics) -> list[float]:
        pass
    
    @abstractmethod
    def get_metric_str(self) -> str:
        pass
    
    @abstractmethod
    def get_y_lim(self) -> Tuple[float, float]:
        pass
    
    def do_draw(self):
        for metric in self.metrics:
            y = self.get_y_metric(metric)
            c1 = mcolors.to_rgb(colors[metric.colreg_s.vessel1.id])
            c2 = mcolors.to_rgb(colors[metric.colreg_s.vessel2.id])
            color = [(c1[0] + c2[0])/2, (c1[1] + c2[1])/2, (c1[2] + c2[2])/2]
            line, = self.ax.plot(range(0, metric.len), y, color=color, linewidth=1.5, label=metric.colreg_s.name, linestyle='-')
            self.line_graphs[metric.colreg_s.name] = line
            self.graphs += [line]
           
        self.ax.margins(x=0.2, y=0.2) 
        self.ax.set_xlim(0, metric.len)
        self.ax.set_ylim(*self.get_y_lim()) 
        self.ax.legend()
        
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        return self.graphs 

class DistanceAxesComponent(AxesComponent):
    def __init__(self, ax : plt.Axes, initial_visibility : bool, env : USVEnvironment, metrics : List[DynamicMetrics]) -> None:
        super().__init__(ax, initial_visibility, env, metrics)  
          
    def get_y_metric(self, metric : DynamicMetrics) -> list[float]:
        return metric.distances
    
    def get_metric_str(self) -> str:
        return 'Distance' 

    def get_y_lim(self) -> Tuple[float, float]:
        return 0, max(self.metrics, key=lambda metric: metric.get_first_distance()).get_first_distance()
    
class DCPAAxesComponent(AxesComponent):
    def __init__(self, ax : plt.Axes, initial_visibility : bool, env : USVEnvironment, metrics : List[DynamicMetrics]) -> None:
        super().__init__(ax, initial_visibility, env, metrics)  
          
    def get_y_metric(self, metric : DynamicMetrics) -> list[float]:
        return metric.dcpas
    
    def get_metric_str(self) -> str:
        return 'DCPA'
    
    def get_y_lim(self) -> Tuple[float, float]:
        return 0, max(self.metrics, key=lambda metric: metric.get_first_dcpa()).get_first_dcpa()
    
class TCPAAxesComponent(AxesComponent):
    def __init__(self, ax : plt.Axes, initial_visibility : bool, env : USVEnvironment, metrics : List[DynamicMetrics]) -> None:
        super().__init__(ax, initial_visibility, env, metrics)  
          
    def get_y_metric(self, metric : DynamicMetrics) -> list[float]:
        return metric.tcpas
    
    def get_metric_str(self) -> str:
        return 'TCPA'
    
    def get_y_lim(self) -> Tuple[float, float]:
        tcpa0 = max(self.metrics, key=lambda metric: metric.get_first_tcpa()).get_first_tcpa()
        return -tcpa0, tcpa0
    