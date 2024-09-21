from typing import List
from matplotlib import patches, pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import BOW_ANGLE, MASTHEAD_LIGHT_ANGLE
from visualization.angle_circle_component import AngleCircleComponent


class CenteredAngleCircleComponent(AngleCircleComponent):
    radius_ratio = 1.7
    def __init__(self, ax: plt.Axes, env : USVEnvironment) -> None:
        super().__init__(ax, env, linewidth=1.8, radius_ratio = self.radius_ratio)
        self.wedge_sterns : List[patches.Wedge]  = []
        self.wedge_bows : List[patches.Wedge]  = []
        self.wedge_mastheads : List[patches.Wedge]  = []
        self.graphs_by_vessel += [self.wedge_sterns, self.wedge_bows, self.wedge_mastheads]          
        
    def do_draw(self):
        for o in self.env.vessels:
            angle1_masthead = np.degrees(o.heading + MASTHEAD_LIGHT_ANGLE / 2)
            angle2_masthead = np.degrees(o.heading - MASTHEAD_LIGHT_ANGLE / 2)
            
            angle1_bow = np.degrees(o.heading + BOW_ANGLE / 2)
            angle2_bow = np.degrees(o.heading - BOW_ANGLE / 2)
            
            # Create the wedge (filled circle slice)
            wedge_stern = patches.Wedge(o.p,
                                        self.angle_circle_radius,
                                        angle1_masthead, angle2_masthead,
                                        color='lightskyblue',
                                        alpha=0.3, zorder=self.zorder)
            self.ax.add_patch(wedge_stern)
            self.wedge_sterns += [wedge_stern]
            
            wedge_bow = patches.Wedge(o.p,
                                    self.angle_circle_radius,
                                    angle2_bow, angle1_bow,
                                    color='hotpink',
                                    alpha=0.3, zorder=self.zorder)
            self.ax.add_patch(wedge_bow)
            self.wedge_bows += [wedge_bow]
            
            wedge_masthead = patches.Wedge(o.p,
                                    self.angle_circle_radius,
                                    angle2_masthead, angle1_masthead,
                                    color='sandybrown',
                                    alpha=0.3, zorder=self.zorder)
            
            self.ax.add_patch(wedge_masthead)
            self.wedge_mastheads += [wedge_masthead]
            
            self.graphs += [wedge_stern, wedge_masthead, wedge_bow]
        super().do_draw()
            
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        for o in new_env.vessels:
            angle1_masthead = np.degrees(o.heading + MASTHEAD_LIGHT_ANGLE / 2)
            angle2_masthead = np.degrees(o.heading - MASTHEAD_LIGHT_ANGLE / 2)
            
            angle1_bow = np.degrees(o.heading + BOW_ANGLE / 2)
            angle2_bow = np.degrees(o.heading - BOW_ANGLE / 2)
            
            self.wedge_sterns[o.id].set_center(o.p)
            self.wedge_sterns[o.id].set_radius(self.angle_circle_radius)
            self.wedge_sterns[o.id].set_theta1(angle1_masthead)
            self.wedge_sterns[o.id].set_theta2(angle2_masthead)
            
            self.wedge_bows[o.id].set_center(o.p)
            self.wedge_bows[o.id].set_radius(self.angle_circle_radius)
            self.wedge_bows[o.id].set_theta1(angle2_bow)
            self.wedge_bows[o.id].set_theta2(angle1_bow)
            
            self.wedge_mastheads[o.id].set_center(o.p)
            self.wedge_mastheads[o.id].set_radius(self.angle_circle_radius)
            self.wedge_mastheads[o.id].set_theta1(angle2_masthead)
            self.wedge_mastheads[o.id].set_theta2(angle1_masthead)
        
        super().do_update(new_env)
        return self.graphs