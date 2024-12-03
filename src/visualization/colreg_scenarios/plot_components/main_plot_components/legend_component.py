from typing import List
from matplotlib import pyplot as plt
from matplotlib.legend import Legend
import numpy as np
from model.environment.usv_environment import LogicalScenario
from model.environment.usv_config import KNOT_TO_MS_CONVERSION
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent

class LegendComponent(PlotComponent):
    
    def __init__(self, ax: plt.Axes, env : LogicalScenario) -> None:
        super().__init__(ax, env)
        self.zorder = 0

    def do_draw(self):
        self.legend : Legend = self.ax.legend()
        self.graphs += [self.legend]
        
    def do_update(self, new_env : LogicalScenario) -> List[plt.Artist]:
        for i, o in enumerate(new_env.vessel_vars):
            # Plot the positions
            dot_label = f'{o}\; p: ({o.p[0]:.1f}, {o.p[1]:.1f}), r: {o.r:.1f} m'
            angle = f'h: {np.degrees(o.heading):.1f}^\circ'
            speed = f'sp: {(o.speed / KNOT_TO_MS_CONVERSION):.1f} kn'
            velocity_label =f'{o}\; {angle}, {speed}'
            
            self.legend.get_texts()[i * 2 + 0].set_text(rf'${dot_label}$') 
            self.legend.get_texts()[i * 2 + 1].set_text(rf'${velocity_label}$') 
        return self.graphs
    