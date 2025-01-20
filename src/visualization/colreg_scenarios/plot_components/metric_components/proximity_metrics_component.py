from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from matplotlib import pyplot as plt
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from evaluation.risk_evaluation import ProximityVector, RiskVector
from utils.asv_utils import N_MILE_TO_M_CONVERSION
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors, light_colors

class ProximityMetricComponent(PlotComponent, ABC):
    time_treshold = 10 * 60
    dist_treshold = 1 * N_MILE_TO_M_CONVERSION
    
    def __init__(self, ax : plt.Axes, scenario: MultiLevelScenario,  risk_vectors : List[RiskVector], ref_risk_vectors : Optional[List[RiskVector]] = None) -> None:
        super().__init__(ax, scenario)
        self.risk_vectors =  risk_vectors
        self. ref_risk_vectors =   ref_risk_vectors
        self.line_graphs : Dict[Tuple[ConcreteVessel, ConcreteVessel], plt.Line2D] = {}
        self.reference_line_graphs : Dict[Tuple[ConcreteVessel, ConcreteVessel], plt.Line2D] = {}
        self.threshold_graphs : Dict[Tuple[ConcreteVessel, ConcreteVessel], plt.Line2D] = {}
        self.ax = ax
        self.length = len(self.risk_vectors)
        
        #self.ax.set_title(self.get_title())
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel(rf'{self.get_metric_str()}')
        self.ax.set_aspect('auto', adjustable='box')      
    
    @abstractmethod
    def get_y_metric(self, proximity_vector : ProximityVector) -> float:
        pass
    
    @abstractmethod
    def get_metric_str(self) -> str:
        pass
    
    @abstractmethod
    def get_threshold_y(self, proximity_vector : ProximityVector) -> float:
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
        x = range(0, self.length)
        for vessel1, vessel2 in self.scenario.os_non_os_pairs:
            if self.length == 0:
                break
            if self.ref_risk_vectors is not None:
                y = [self.get_y_metric(rv.proximity_vectors[(vessel1, vessel2)]) for rv in self.ref_risk_vectors if (vessel1, vessel2) in rv.proximity_vectors]
                line, = self.ax.plot(x, y, color=light_colors[vessel2.id], linewidth=2, linestyle=':')
                self.reference_line_graphs[(vessel1, vessel2)] = line
                self.graphs += [line]
            
            threshold_y = [self.get_threshold_y(self.risk_vectors[0].proximity_vectors[(vessel1, vessel2)])] * self.length
            y = [self.get_y_metric(rv.proximity_vectors[(vessel1, vessel2)]) for rv in self.risk_vectors if (vessel1, vessel2) in rv.proximity_vectors]
            line, = self.ax.plot(x, y, color=colors[vessel2.id],
                                linewidth=1.7, label=fr'${self.scenario.get_vessel_name(vessel1)} \rightarrow {self.scenario.get_vessel_name(vessel2)}$', linestyle='-')
            #threshold, = self.ax.plot(x, threshold_y, color=light_colors[vessel2.id], linewidth=1, linestyle='--')
            self.line_graphs[(vessel1, vessel2)] = line
            #self.threshold_graphs[(vessel1, vessel2)] = threshold
            self.graphs += [line]
        
            
        threshold2, = self.ax.plot(x, [self.get_threshold2_y()] * self.length, color='black', linewidth=1.5, linestyle='--')
        threshold2, = self.ax.plot(x, [0] * self.length, color='black', linewidth=1.5, linestyle='--')
        self.threshold_graphs['basic'] = threshold2
        self.graphs += [threshold2]
           
        self.ax.margins(x=0.2, y=0.2) 
        self.ax.set_xlim(0, self.length)
        self.ax.set_ylim(*self.get_y_lim()) 
        self.ax.legend()
        
        ymin, ymax = self.ax.get_ylim()
        offset = (ymax - ymin) * 0.03  # 5% of the y-axis range
        self.ax.text(self.length / 2, self.get_threshold2_y() + offset, self.get_threshold2_label(), ha='center', va='center', fontsize=11, horizontalalignment='center')  
        
    def do_update(self, scene : ConcreteScene) -> List[plt.Artist]:
        return self.graphs 

class DistanceAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes, scenario: MultiLevelScenario,  risk_vectors : List[RiskVector],   ref_risk_vectors : Optional[List[RiskVector]] = None) -> None:
        super().__init__(ax, scenario,  risk_vectors,   ref_risk_vectors)  
          
    def get_y_metric(self, proximity_vector : ProximityVector) -> float:
        return proximity_vector.dist
    
    def get_metric_str(self) -> str:
        return 'Distance (m)'
    
    def get_title(self) -> str:
        return 'Distance'

    def get_y_lim(self) -> Tuple[float, float]:
        dist = max(self.risk_vectors[0].proximity_vectors.values(), key=lambda pv: pv.dist).dist
        return -0.1, max(dist*2, self.get_threshold2_y()*1.1)
    
    def get_threshold_y(self, proximity_vector : ProximityVector) -> float:
        return proximity_vector.props.safety_dist
    
    def get_threshold2_y(self) -> float:
        return self.dist_treshold
    
    def get_threshold2_label(self) -> str:
        return f'{(self.dist_treshold / N_MILE_TO_M_CONVERSION):.0f} NM'
    
class DCPAAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes, scenario: MultiLevelScenario,  risk_vectors : List[RiskVector],   ref_risk_vectors : Optional[List[RiskVector]] = None) -> None:
        super().__init__(ax, scenario,  risk_vectors,   ref_risk_vectors)  
          
    def get_y_metric(self, proximity_vector : ProximityVector) -> float:
        return proximity_vector.dcpa
    
    def get_metric_str(self) -> str:
        return 'DCPA (m)'
    
    def get_title(self) -> str:
        return 'Distance at closest point of approach'
    
    def get_y_lim(self) -> Tuple[float, float]:
        dcpa = max(self.risk_vectors[0].proximity_vectors.values(), key=lambda pv: pv.dcpa).dcpa
        #threshold = max(self.metrics, key=lambda metric: metric.relation.safety_dist).relation.safety_dist
        return -0.1, max(dcpa * 2, self.get_threshold2_y()*1.1)
    
    def get_threshold_y(self, proximity_vector : ProximityVector) -> float:
        return proximity_vector.props.safety_dist
    
    def get_threshold2_y(self) -> float:
        return self.dist_treshold
    
    def get_threshold2_label(self) -> str:
        return f'{(self.dist_treshold / N_MILE_TO_M_CONVERSION):.0f} NM'
    
class TCPAAxesComponent(ProximityMetricComponent):
    def __init__(self, ax : plt.Axes, scenario: MultiLevelScenario,  risk_vectors : List[RiskVector],   ref_risk_vectors : Optional[List[RiskVector]] = None) -> None:
        super().__init__(ax, scenario,  risk_vectors,   ref_risk_vectors)  
          
    def get_y_metric(self, proximity_vector : ProximityVector) -> float:
        return proximity_vector.tcpa
    
    def get_metric_str(self) -> str:
        return 'TCPA (s)'
    
    def get_title(self) -> str:
        return 'Time to closest point of approach'
    
    def get_y_lim(self) -> Tuple[float, float]:
        tcpa0 = max(self.risk_vectors[0].proximity_vectors.values(), key=lambda pv: pv.tcpa).tcpa
        return -100, max(tcpa0, self.get_threshold2_y()) * 1.1
    
    def get_threshold_y(self, proximity_vector : ProximityVector) -> float:
        return 0.0
    
    def get_threshold2_y(self) -> float:
        return self.time_treshold
    
    def get_threshold2_label(self) -> str:
        return f'{(self.time_treshold / 60):.0f} min'
    