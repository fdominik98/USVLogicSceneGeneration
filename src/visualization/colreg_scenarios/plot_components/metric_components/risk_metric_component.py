from typing import Dict, List, Optional
from matplotlib import pyplot as plt
from logical_level.models.logical_scenario import LogicalScenario
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors, light_colors

class RiskMetricComponent(PlotComponent):
    def __init__(self, ax : plt.Axes,logical_scenario: LogicalScenario, metrics : Dict[int, List[float]], y_label : str, x_label : bool, reference_metrics : Optional[Dict[int, List[float]]] = None) -> None:
        super().__init__(ax, env)
        self.metrics = metrics
        self.reference_metrics = reference_metrics
        self.line_graphs : Dict[int, plt.Line2D] = {}
        self.reference_line_graphs : Dict[int, plt.Line2D] = {}
        self.ax = ax
        
        #self.ax.set_title('Collision risk evolution')
        if x_label:
            self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel(y_label)
        self.ax.set_aspect('auto', adjustable='box')      
    
    def do_draw(self):
        if self.reference_metrics is not None:
            for id, metric in self.reference_metrics.items():
                if len(metric) == 0:
                    continue
                vessel = self.logical_scenario.get_vessel_by_id(id)
                x = range(0, len(metric))
                line, = self.ax.plot(x, metric, color=light_colors[id], linestyle=':', label=f'{vessel.name} no intervention', linewidth=2)
                self.reference_line_graphs[id] = line
                self.graphs += [line]
                
                
        for id, metric in self.metrics.items():
            if len(metric) == 0:
                continue
            vessel = self.logical_scenario.get_vessel_by_id(id)
            x = range(0, len(metric))
            line, = self.ax.plot(x, metric, color=colors[id], linewidth=1.7, label=f'{vessel.name} COLREGS compliant', linestyle='-')
            self.line_graphs[id] = line
            self.graphs += [line]   
           
        self.ax.margins(x=0.2, y=0.2) 
        longest = max(list(self.metrics.values()), key=len)
        self.ax.set_xlim(0, len(longest))
        self.ax.set_ylim(-0.05, 1.05) 
        self.ax.legend()
        
    def do_update(self, new_env : LogicalScenario) -> List[plt.Artist]:
        return self.graphs