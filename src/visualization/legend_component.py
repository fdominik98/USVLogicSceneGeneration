from typing import List
from matplotlib import pyplot as plt
from matplotlib.legend import Legend
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import KNOT_TO_MS_CONVERSION
from visualization.plot_component import PlotComponent

class LegendComponent(PlotComponent):
    
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)

    def do_draw(self, zorder : int):
        self.legend : Legend = self.ax.legend()
        self.graphs += [self.legend]
        
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        for i, o in enumerate(new_env.vessels):
            pos_label = f'{o} Position: ({o.p[0]:.2f}, {o.p[1]:.2f})'
            self.legend.get_texts()[i * 3 + 1].set_text(pos_label) 
            angle = fr'$\theta = {np.degrees(o.heading):.2f}^\circ$'
            speed = f'speed = {(o.speed / KNOT_TO_MS_CONVERSION):.2f}kn'
            velocity_label =f'{o} Velocity: {angle}, {speed}'
            self.legend.get_texts()[i * 3 + 2].set_text(velocity_label) 
        return self.graphs
    