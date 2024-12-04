from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from matplotlib import pyplot as plt
from logical_level.models.logical_scenario import LogicalScenario
from asv_utils import N_MILE_TO_M_CONVERSION
from evaluation.proximity_evaluator import TrajProximityMetric
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors, light_colors

class ProximityMetricComponent(PlotComponent, ABC):
    time_treshold = 10 * 60
    dist_treshold = 1 * N_MILE_TO_M_CONVERSION
    
    def __init__(self, ax : plt.Axes,logical_scenario: LogicalScenario, metrics : List[TrajProximityMetric], reference_metrics : Optional[List[TrajProximityMetric]] = None) -> None:
        super().__init__(ax, env)
        self.metrics = metrics
        self.reference_metrics = reference_metrics
        self.line_graphs : Dict[str, plt.Line2D] = {}
        self.reference_line_graphs : Dict[str, plt.Line2D] = {}
        self.threshold_graphs : Dict[str, plt.Line2D] = {}
        self.ax = ax
        
        #self.ax.set_title(self.get_title())
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel(rf'{self.get_metric_str()}')
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
    def get_threshold2_y(self) -> float:
        pass
    
    @abstractmethod
    def get_threshold2_label(self) -> str:
        pass
    
    @abstractmethod
    def get_y_lim(self) -> Tuple[float, float]:
        pass
    
    @abstractmethod
    def get_title(self) -> str:
        pass
    
    def do_draw(self):
        if self.reference_metrics is not None:
            for metric in self.reference_metrics:
                ts_vessel = metric.relation.vessel1 if metric.relation.vessel1.id != 0 else metric.relation.vessel2
                y = self.get_y_metric(metric)
                x = range(0, metric.len)
                line, = self.ax.plot(x, y, color=light_colors[ts_vessel.id], linewidth=2, linestyle=':')
                self.reference_line_graphs[metric.relation.name] = line
                self.graphs += [line]
        
        
        for metric in self.metrics:
            ts_vessel = metric.relation.vessel1 if metric.relation.vessel1.id != 0 else metric.relation.vessel2
            threshold_y = self.get_threshold_y(metric)
            y = self.get_y_metric(metric)
            x = range(0, metric.len)
            line, = self.ax.plot(x, y, color=colors[ts_vessel.id],
                                 linewidth=1.7, label=fr'${metric.relation.vessel1} \rightarrow {metric.relation.vessel2}$', linestyle='-')
            #threshold, = self.ax.plot(x, threshold_y, color=light_colors[ts_vessel.id], linewidth=1, linestyle='--')
            self.line_graphs[metric.relation.name] = line
            #self.threshold_graphs[metric.relation.name] = threshold
            self.graphs += [line]
            
        threshold2, = self.ax.plot(x, [self.get_threshold2_y()] * metric.len, color='black', linewidth=1.5, linestyle='--')
        threshold2, = self.ax.plot(x, [0] * metric.len, color='black', linewidth=1.5, linestyle='--')
        self.threshold_graphs['basic'] = threshold2
        self.graphs += [threshold2]
           
        self.ax.margins(x=0.2, y=0.2) 
        self.ax.set_xlim(0, metric.len)
        self.ax.set_ylim(*self.get_y_lim()) 
        self.ax.legend()
        
        ymin, ymax = self.ax.get_ylim()
        offset = (ymax - ymin) * 0.03  # 5% of the y-axis range
        self.ax.text(metric.len / 2, self.get_threshold2_y() + offset, self.get_threshold2_label(), ha='center', va='center', fontsize=11, horizontalalignment='center')  
        
    def do_update(self, new_env : LogicalScenario) -> List[plt.Artist]:
        return self.graphs 

class DistanceAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes,logical_scenario: LogicalScenario, metrics : List[TrajProximityMetric], reference_metrics : Optional[List[TrajProximityMetric]] = None) -> None:
        super().__init__(ax, logical_scenario, metrics, reference_metrics)  
          
    def get_y_metric(self, metric : TrajProximityMetric) -> list[float]:
        return [vec.dist for vec in metric.vectors]
    
    def get_metric_str(self) -> str:
        return 'Distance (m)'
    
    def get_title(self) -> str:
        return 'Distance'

    def get_y_lim(self) -> Tuple[float, float]:
        dist = max(self.metrics, key=lambda metric: metric.get_first_distance()).get_first_distance()
        return -0.1, max(dist*2, self.get_threshold2_y()*1.1)
    
    def get_threshold_y(self, metric : TrajProximityMetric) -> list[float]:
        return [metric.relation.safety_dist] * metric.len
    
    def get_threshold2_y(self) -> float:
        return self.dist_treshold
    
    def get_threshold2_label(self) -> str:
        return f'{(self.dist_treshold / N_MILE_TO_M_CONVERSION):.0f} NM'
    
class DCPAAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes,logical_scenario: LogicalScenario, metrics : List[TrajProximityMetric], reference_metrics : Optional[List[TrajProximityMetric]] = None) -> None:
        super().__init__(ax, logical_scenario, metrics, reference_metrics)  
          
    def get_y_metric(self, metric : TrajProximityMetric) -> list[float]:
        return [vec.dcpa for vec in metric.vectors]
    
    def get_metric_str(self) -> str:
        return 'DCPA (m)'
    
    def get_title(self) -> str:
        return 'Distance at closest point of approach'
    
    def get_y_lim(self) -> Tuple[float, float]:
        dcpa = max(self.metrics, key=lambda metric: metric.get_first_dcpa()).get_first_dcpa()
        #threshold = max(self.metrics, key=lambda metric: metric.relation.safety_dist).relation.safety_dist
        return -0.1, max(dcpa * 2, self.get_threshold2_y()*1.1)
    
    def get_threshold_y(self, metric : TrajProximityMetric) -> list[float]:
        return [metric.relation.safety_dist] * metric.len
    
    def get_threshold2_y(self) -> float:
        return self.dist_treshold
    
    def get_threshold2_label(self) -> str:
        return f'{(self.dist_treshold / N_MILE_TO_M_CONVERSION):.0f} NM'
    
class TCPAAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes,logical_scenario: LogicalScenario, metrics : List[TrajProximityMetric], reference_metrics : Optional[List[TrajProximityMetric]] = None) -> None:
        super().__init__(ax, logical_scenario, metrics, reference_metrics)  
          
    def get_y_metric(self, metric : TrajProximityMetric) -> list[float]:
        return [vec.tcpa for vec in metric.vectors]
    
    def get_metric_str(self) -> str:
        return 'TCPA (s)'
    
    def get_title(self) -> str:
        return 'Time to closest point of approach'
    
    def get_y_lim(self) -> Tuple[float, float]:
        tcpa0 = max(self.metrics, key=lambda metric: metric.get_first_tcpa()).get_first_tcpa()
        return -100, max(tcpa0, self.get_threshold2_y()) * 1.1
    
    def get_threshold_y(self, metric : TrajProximityMetric) -> list[float]:
        return [0] * metric.len
    
    def get_threshold2_y(self) -> float:
        return self.time_treshold
    
    def get_threshold2_label(self) -> str:
        return f'{(self.time_treshold / 60):.0f} min'
    