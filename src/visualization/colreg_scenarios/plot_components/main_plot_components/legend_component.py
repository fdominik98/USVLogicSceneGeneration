from typing import List
from matplotlib import pyplot as plt
from matplotlib.legend import Legend
import numpy as np
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from utils.asv_utils import KNOT_TO_MS_CONVERSION
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent

class LegendComponent(PlotComponent):
    
    def __init__(self, ax : plt.Axes, scenario : MultiLevelScenario) -> None:
        super().__init__(ax, scenario)
        self.zorder = 0

    def do_draw(self):
        self.legend : Legend = self.ax.legend()
        self.graphs += [self.legend]
        
    def do_update(self, scene : ConcreteScene) -> List[plt.Artist]:
        for i, (vessel, state) in enumerate(scene.items()):
            # Plot the positions
            dot_label = f'{vessel}\; p: ({state.p[0]:.1f}, {state.p[1]:.1f}), r: {vessel.radius:.1f} m'
            angle = f'h: {np.degrees(state.heading):.1f}^\circ'
            speed = f'sp: {(state.speed / KNOT_TO_MS_CONVERSION):.1f} kn'
            velocity_label =f'{vessel}\; {angle}, {speed}'
            
            self.legend.get_texts()[i * 2 + 0].set_text(rf'${dot_label}$') 
            self.legend.get_texts()[i * 2 + 1].set_text(rf'${velocity_label}$') 
        return self.graphs
    