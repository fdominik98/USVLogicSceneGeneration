from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from matplotlib import pyplot as plt
from model.environment.usv_environment import USVEnvironment
from trajectory_planning.proximity_evaluator import TrajProximityMetric
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors, light_colors

class ProximityMetricComponent(PlotComponent, ABC):
    def __init__(self, ax : plt.Axes, env : USVEnvironment, metrics : List[TrajProximityMetric]) -> None:
        super().__init__(ax, env)
        self.metrics = metrics
        self.line_graphs : Dict[str, plt.Line2D] = {}
        self.threshold_graphs : Dict[str, plt.Line2D] = {}
        self.ax = ax
        
        self.ax.set_title(self.get_title())
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel(f'{self.get_metric_str()} (m)')
        self.ax.set_aspect('auto', adjustable='box')      
    
    @abstractmethod
    def get_y_metric(self, metric : TrajProximityMetric) -> list[float]:
        pass
    
    @abstractmethod
    def get_metric_str(self) -> str:
        pass
    
    @abstractmethod
    def get_threshold_y(self, metric : TrajProximityMetric) -> list[float]:
        pass
    
    @abstractmethod
    def get_y_lim(self) -> Tuple[float, float]:
        pass
    
    @abstractmethod
    def get_title(self) -> str:
        pass
    
    def do_draw(self):
        for metric in self.metrics:
            ts_vessel = metric.relation.vessel1 if metric.relation.vessel1.id != 0 else metric.relation.vessel2
            threshold_y = self.get_threshold_y(metric)
            y = self.get_y_metric(metric)
            x = range(0, metric.len)
            line, = self.ax.plot(x, y, color=colors[ts_vessel.id], linewidth=1.5, label=metric.relation.name, linestyle='-')
            threshold, = self.ax.plot(x, threshold_y, color=light_colors[ts_vessel.id], linewidth=1, linestyle='--')
            self.line_graphs[metric.relation.name] = line
            self.threshold_graphs[metric.relation.name] = threshold
            self.graphs += [line, threshold]
           
        self.ax.margins(x=0.2, y=0.2) 
        self.ax.set_xlim(0, metric.len)
        self.ax.set_ylim(*self.get_y_lim()) 
        self.ax.legend()
        
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        return self.graphs 

class DistanceAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes, env : USVEnvironment, metrics : List[TrajProximityMetric]) -> None:
        super().__init__(ax, env, metrics)  
          
    def get_y_metric(self, metric : TrajProximityMetric) -> list[float]:
        return [vec.dist for vec in metric.vectors]
    
    def get_metric_str(self) -> str:
        return 'Distance'
    
    def get_title(self) -> str:
        return 'Distance'

    def get_y_lim(self) -> Tuple[float, float]:
        dist = max(self.metrics, key=lambda metric: metric.get_first_distance()).get_first_distance()
        return 0, dist*2
    
    def get_threshold_y(self, metric : TrajProximityMetric) -> list[float]:
        return [metric.relation.safety_dist] * metric.len
    
class DCPAAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes, env : USVEnvironment, metrics : List[TrajProximityMetric]) -> None:
        super().__init__(ax, env, metrics)  
          
    def get_y_metric(self, metric : TrajProximityMetric) -> list[float]:
        return [vec.dcpa for vec in metric.vectors]
    
    def get_metric_str(self) -> str:
        return 'DCPA'
    
    def get_title(self) -> str:
        return 'Distance at closest point of approach'
    
    def get_y_lim(self) -> Tuple[float, float]:
        dcpa = max(self.metrics, key=lambda metric: metric.get_first_dcpa()).get_first_dcpa()
        threshold = max(self.metrics, key=lambda metric: metric.relation.safety_dist).relation.safety_dist
        return 0, max(dcpa * 2, threshold*1.1)
    
    def get_threshold_y(self, metric : TrajProximityMetric) -> list[float]:
        return [metric.relation.safety_dist] * metric.len
    
class TCPAAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes, env : USVEnvironment, metrics : List[TrajProximityMetric]) -> None:
        super().__init__(ax, env, metrics)  
          
    def get_y_metric(self, metric : TrajProximityMetric) -> list[float]:
        return [vec.tcpa for vec in metric.vectors]
    
    def get_metric_str(self) -> str:
        return 'TCPA'
    
    def get_title(self) -> str:
        return 'Time to closest point of approach'
    
    def get_y_lim(self) -> Tuple[float, float]:
        tcpa0 = max(self.metrics, key=lambda metric: metric.get_first_tcpa()).get_first_tcpa()
        return 0, tcpa0 * 2
    
    def get_threshold_y(self, metric : TrajProximityMetric) -> list[float]:
        return [0] * metric.len
    