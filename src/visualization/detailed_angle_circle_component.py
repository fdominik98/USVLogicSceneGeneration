from matplotlib import patches, pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import CROSSING_ANGLE, HEAD_ON_ANGLE, MASTHEAD_ANGLE, MAX_COORD, OVERTAKE_ANGLE
from visualization.angle_circle_component import AngleCircleComponent
from visualization.plot_component import PlotComponent, light_colors


class DetailedAngleCircleComponent(AngleCircleComponent):
    radius_ratio = 2
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env, linewidth=3, radius_ratio = self.radius_ratio, only_os=True)
            
    def do_draw(self, zorder : int):
        
        os = self.env.vessels[0]
        
        angle1_masthead = np.degrees(os.heading + MASTHEAD_ANGLE / 2)
        angle2_masthead = np.degrees(os.heading - MASTHEAD_ANGLE / 2)
        
        # Create the wedge (filled circle slice)
        wedge_overtake = patches.Wedge(os.p - os.v_norm() * self.angle_circle_radius * 0.05,
                                       self.angle_circle_radius * 0.90,
                                       angle1_masthead, angle2_masthead,
                                       color=light_colors[1],
                                       alpha=0.3, zorder=zorder)
        self.ax.add_patch(wedge_overtake)
        
        wedge_masthead = patches.Wedge(os.p + os.v_norm() * self.angle_circle_radius * 0.05,
                                self.angle_circle_radius * 0.90,
                                angle2_masthead, angle1_masthead,
                                color=light_colors[3],
                                alpha=0.3, zorder=zorder)
        
        self.ax.add_patch(wedge_masthead)
        self.graphs += [wedge_overtake, wedge_masthead]
        super().do_draw(zorder)
            
