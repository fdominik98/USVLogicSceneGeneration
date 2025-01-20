from typing import Dict, List, Optional
from matplotlib import pyplot as plt
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from evaluation.risk_evaluation import RiskVector
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors, light_colors

class RiskMetricComponent(PlotComponent):
    def __init__(self, ax : plt.Axes, scenario: MultiLevelScenario, risk_vectors : List[RiskVector], y_label : str, x_label : bool, ref_risk_vectors : Optional[List[RiskVector]] = None) -> None:
        super().__init__(ax, scenario)
        self.risk_vectors = risk_vectors
        self.ref_risk_vectors = ref_risk_vectors
        self.line_graphs : Dict[ConcreteVessel, plt.Line2D] = {}
        self.reference_line_graphs : Dict[ConcreteVessel, plt.Line2D] = {}
        self.ax = ax
        self.length = len(self.risk_vectors)
        
        #self.ax.set_title('Collision risk evolution')
        if x_label:
            self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel(y_label)
        self.ax.set_aspect('auto', adjustable='box')      
    
    def do_draw(self):
        x = range(0, self.length)
        for vessel in self.scenario.concrete_scene.actors:
            if self.length == 0:
                break
            if self.ref_risk_vectors is not None:
                y = [rv.danger_sectors[vessel] for rv in self.ref_risk_vectors if vessel in rv.danger_sectors]
                line, = self.ax.plot(x, y, color=light_colors[vessel.id], linestyle=':', label=f'{self.scenario.get_vessel_name(vessel)} no intervention', linewidth=2)
                self.reference_line_graphs[vessel] = line
                self.graphs += [line]
            
            y = [rv.danger_sectors[vessel] for rv in self.risk_vectors if vessel in rv.danger_sectors]
            line, = self.ax.plot(x, y, color=colors[vessel.id], linewidth=1.7, label=f'{self.scenario.get_vessel_name(vessel)} COLREGS compliant', linestyle='-')
            self.line_graphs[vessel] = line
            self.graphs += [line]   
            
        self.ax.margins(x=0.2, y=0.2) 
        self.ax.set_xlim(0, self.length)
        self.ax.set_ylim(-0.05, 1.05) 
        self.ax.legend()
        
    def do_update(self, scene : ConcreteScene) -> List[plt.Artist]:
        return self.graphs