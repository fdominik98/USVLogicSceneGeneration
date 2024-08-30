from matplotlib import patches, pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import BOW_ANGLE, MASTHEAD_LIGHT_ANGLE
from visualization.angle_circle_component import AngleCircleComponent


class CenteredAngleCircleComponent(AngleCircleComponent):
    radius_ratio = 1.7
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment, center_vessel_id = 0) -> None:
        super().__init__(ax, initial_visibility, env, linewidth=1.5, radius_ratio = self.radius_ratio, center_vessel_id=center_vessel_id)
        self.center_vessel_id = center_vessel_id
            
    def do_draw(self, zorder : int):
        
        o = self.env.vessels[self.center_vessel_id]
        
        angle1_masthead = np.degrees(o.heading + MASTHEAD_LIGHT_ANGLE / 2)
        angle2_masthead = np.degrees(o.heading - MASTHEAD_LIGHT_ANGLE / 2)
        
        angle1_bow = np.degrees(o.heading + BOW_ANGLE / 2)
        angle2_bow = np.degrees(o.heading - BOW_ANGLE / 2)
        
        # Create the wedge (filled circle slice)
        self.wedge_stern = patches.Wedge(o.p,
                                       self.angle_circle_radius * 0.95,
                                       angle1_masthead, angle2_masthead,
                                       color='lightskyblue',
                                       alpha=0.3, zorder=zorder)
        self.ax.add_patch(self.wedge_stern)
        
        self.wedge_bow = patches.Wedge(o.p,
                                self.angle_circle_radius * 0.95,
                                angle2_bow, angle1_bow,
                                color='hotpink',
                                alpha=0.3, zorder=zorder)
        self.ax.add_patch(self.wedge_bow)
        
        self.wedge_masthead = patches.Wedge(o.p,
                                self.angle_circle_radius * 0.95,
                                angle2_masthead, angle1_masthead,
                                color='sandybrown',
                                alpha=0.3, zorder=zorder)
        
        self.ax.add_patch(self.wedge_masthead)
        self.graphs += [self.wedge_stern, self.wedge_masthead, self.wedge_bow]
        super().do_draw(zorder)
            
    def update(self, new_env : USVEnvironment) -> list[plt.Artist]:
        o = new_env.vessels[self.center_vessel_id]
        
        angle1_masthead = np.degrees(o.heading + MASTHEAD_LIGHT_ANGLE / 2)
        angle2_masthead = np.degrees(o.heading - MASTHEAD_LIGHT_ANGLE / 2)
        
        angle1_bow = np.degrees(o.heading + BOW_ANGLE / 2)
        angle2_bow = np.degrees(o.heading - BOW_ANGLE / 2)
        
        self.wedge_stern.set_center(o.p)
        self.wedge_stern.set_radius(self.angle_circle_radius * 0.95)
        self.wedge_stern.set_theta1(angle1_masthead)
        self.wedge_stern.set_theta2(angle2_masthead)
        
        self.wedge_bow.set_center(o.p)
        self.wedge_bow.set_radius(self.angle_circle_radius * 0.95)
        self.wedge_bow.set_theta1(angle2_bow)
        self.wedge_bow.set_theta2(angle1_bow)
        
        self.wedge_masthead.set_center(o.p)
        self.wedge_masthead.set_radius(self.angle_circle_radius * 0.95)
        self.wedge_masthead.set_theta1(angle2_masthead)
        self.wedge_masthead.set_theta2(angle1_masthead)
        
        self.update_one(o)
        return self.graphs