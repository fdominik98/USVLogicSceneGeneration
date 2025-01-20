from typing import Dict, List
from matplotlib import patches, pyplot as plt
import numpy as np
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from utils.asv_utils import BOW_ANGLE, MASTHEAD_LIGHT_ANGLE
from visualization.colreg_scenarios.plot_components.main_plot_components.angle_circle_component import AngleCircleComponent


class CenteredAngleCircleComponent(AngleCircleComponent):
    radius_ratio = 1.7
    def __init__(self, ax : plt.Axes, scenario : MultiLevelScenario) -> None:
        super().__init__(ax, scenario, linewidth=2.0, radius_ratio = self.radius_ratio)
        self.wedge_sterns : Dict[ConcreteVessel, patches.Wedge]  = {}
        self.wedge_bows : Dict[ConcreteVessel, patches.Wedge]  = {}
        self.wedge_mastheads : Dict[ConcreteVessel, patches.Wedge] = {}
        self.graphs_by_vessel += [self.wedge_sterns, self.wedge_bows, self.wedge_mastheads]          
        
    def do_draw(self):
        for vessel, state in self.scenario.concrete_scene.items():
            angle1_masthead = np.degrees(state.heading + MASTHEAD_LIGHT_ANGLE / 2)
            angle2_masthead = np.degrees(state.heading - MASTHEAD_LIGHT_ANGLE / 2)
            
            angle1_bow = np.degrees(state.heading + BOW_ANGLE / 2)
            angle2_bow = np.degrees(state.heading - BOW_ANGLE / 2)
            
            # Create the wedge (filled circle slice)
            wedge_stern = patches.Wedge(state.p,
                                        self.angle_circle_radius,
                                        angle1_masthead, angle2_masthead,
                                        color='lightskyblue',
                                        alpha=0.3, zorder=self.zorder)
            self.ax.add_patch(wedge_stern)
            self.wedge_sterns[vessel] = wedge_stern
            
            wedge_bow = patches.Wedge(state.p,
                                    self.angle_circle_radius,
                                    angle2_bow, angle1_bow,
                                    color='hotpink',
                                    alpha=0.3, zorder=self.zorder)
            self.ax.add_patch(wedge_bow)
            self.wedge_bows[vessel] = wedge_bow
            
            wedge_masthead = patches.Wedge(state.p,
                                    self.angle_circle_radius,
                                    angle2_masthead, angle1_masthead,
                                    color='sandybrown',
                                    alpha=0.3, zorder=self.zorder)
            
            self.ax.add_patch(wedge_masthead)
            self.wedge_mastheads[vessel] = wedge_masthead
            
            self.graphs += [wedge_stern, wedge_masthead, wedge_bow]
        super().do_draw()
            
    def do_update(self, scene : ConcreteScene) -> List[plt.Artist]:
        for vessel, state in scene.items():
            angle1_masthead = np.degrees(state.heading + MASTHEAD_LIGHT_ANGLE / 2)
            angle2_masthead = np.degrees(state.heading - MASTHEAD_LIGHT_ANGLE / 2)
            
            angle1_bow = np.degrees(state.heading + BOW_ANGLE / 2)
            angle2_bow = np.degrees(state.heading - BOW_ANGLE / 2)
            
            self.wedge_sterns[vessel].set_center(state.p)
            self.wedge_sterns[vessel].set_radius(self.angle_circle_radius)
            self.wedge_sterns[vessel].set_theta1(angle1_masthead)
            self.wedge_sterns[vessel].set_theta2(angle2_masthead)
            
            self.wedge_bows[vessel].set_center(state.p)
            self.wedge_bows[vessel].set_radius(self.angle_circle_radius)
            self.wedge_bows[vessel].set_theta1(angle2_bow)
            self.wedge_bows[vessel].set_theta2(angle1_bow)
            
            self.wedge_mastheads[vessel].set_center(state.p)
            self.wedge_mastheads[vessel].set_radius(self.angle_circle_radius)
            self.wedge_mastheads[vessel].set_theta1(angle2_masthead)
            self.wedge_mastheads[vessel].set_theta2(angle1_masthead)
        
        super().do_update(scene)
        return self.graphs