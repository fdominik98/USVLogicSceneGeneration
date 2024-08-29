from matplotlib import patches, pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import BEAM_ANGLE, BOW_ANGLE, MASTHEAD_LIGHT_ANGLE, MAX_COORD, STERN_ANGLE
from visualization.angle_circle_component import AngleCircleComponent


class CenteredAngleCircleComponent(AngleCircleComponent):
    radius_ratio = 1.7
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment, center_vessel_id = 0) -> None:
        super().__init__(ax, initial_visibility, env, linewidth=1.5, radius_ratio = self.radius_ratio, center_vessel_id=center_vessel_id)
        self.center_vessel_id = center_vessel_id
            
    def do_draw(self, zorder : int):
        
        os = self.env.vessels[self.center_vessel_id]
        
        angle1_masthead = np.degrees(os.heading + MASTHEAD_LIGHT_ANGLE / 2)
        angle2_masthead = np.degrees(os.heading - MASTHEAD_LIGHT_ANGLE / 2)
        
        angle1_bow = np.degrees(os.heading + BOW_ANGLE / 2)
        angle2_bow = np.degrees(os.heading - BOW_ANGLE / 2)
        
        # Create the wedge (filled circle slice)
        wedge_stern = patches.Wedge(os.p,
                                       self.angle_circle_radius * 0.95,
                                       angle1_masthead, angle2_masthead,
                                       color='lightskyblue',
                                       alpha=0.3, zorder=zorder)
        self.ax.add_patch(wedge_stern)
        
        wedge_bow = patches.Wedge(os.p,
                                self.angle_circle_radius * 0.95,
                                angle2_bow, angle1_bow,
                                color='hotpink',
                                alpha=0.3, zorder=zorder)
        self.ax.add_patch(wedge_bow)
        
        wedge_masthead = patches.Wedge(os.p,
                                self.angle_circle_radius * 0.95,
                                angle2_masthead, angle1_masthead,
                                color='sandybrown',
                                alpha=0.3, zorder=zorder)
        
        self.ax.add_patch(wedge_masthead)
        self.graphs += [wedge_stern, wedge_masthead, wedge_bow]
        super().do_draw(zorder)
            
