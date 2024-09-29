from typing import Dict, List
from matplotlib import pyplot as plt
from model.environment.usv_environment import USVEnvironment
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors

class RiskMetricComponent(PlotComponent):
    def __init__(self, ax : plt.Axes, env : USVEnvironment, metrics : Dict[int, List[float]]) -> None:
        super().__init__(ax, env)
        self.metrics = metrics
        self.line_graphs : Dict[int, plt.Line2D] = {}
        self.ax = ax
        
        self.ax.set_title('Collision risk evolution')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel(f'Collision risk (m)')
        self.ax.set_aspect('auto', adjustable='box')      
    
    def do_draw(self):
        for id, metric in self.metrics.items():
            if len(metric) == 0:
                continue
            vessel = self.env.get_vessel_by_id(id)
            x = range(0, len(metric))
            line, = self.ax.plot(x, metric, color=colors[id], linewidth=1.5, label=vessel.name, linestyle='-')
            self.line_graphs[id] = line
            self.graphs += [line]
           
        self.ax.margins(x=0.2, y=0.2) 
        longest = max(list(self.metrics.values()), key=len)
        self.ax.set_xlim(0, len(longest))
        self.ax.set_ylim(0, 1) 
        self.ax.legend()
        
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        return self.graphs