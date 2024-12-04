from typing import Dict, List
from matplotlib import pyplot as plt
import numpy as np
from logical_level.models.logical_scenario import LogicalScenario
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent


class AdditionalVOConeComponent(PlotComponent):
    def __init__(self, ax: plt.Axes,logical_scenario: LogicalScenario) -> None:
        super().__init__(ax, env)
        self.circle_graphs : Dict[str, plt.Circle] = {}
        self.line1_graphs : Dict[str, plt.Line2D] = {}
        self.line2_graphs : Dict[str, plt.Line2D] = {}
        self.graphs_by_rels = [self.circle_graphs, self.line1_graphs, self.line2_graphs]
        self.zorder = -2
            
    def do_draw(self):
        for rel in self.logical_scenario.relations:
            if rel.vessel2.is_OS():
                o1 = rel.vessel2
                o2 = rel.vessel1
                p12 = rel.p21
            else:
                o1 = rel.vessel1
                o2 = rel.vessel2
                p12 = rel.p12
            vo_circle = plt.Circle(o2.p, rel.safety_dist, color='black', fill=False, linestyle='--', linewidth=0.7, zorder=self.zorder)
            self.ax.add_artist(vo_circle)
            self.circle_graphs[rel.name] = vo_circle
            # Calculate the angles of the cone
            angle_rel = np.arctan2(p12[1], p12[0])
            sin_half_cone_theta = np.clip(rel.safety_dist / rel.o_distance, -1, 1)
            angle_half_cone = abs(np.arcsin(sin_half_cone_theta)) # [0, pi/2] 
            angle1 = angle_rel + angle_half_cone
            angle2 = angle_rel - angle_half_cone
            
            # Plot the velocity obstacle cone
            cone1 = o1.p + np.array([np.cos(angle1), np.sin(angle1)]) * rel.o_distance
            cone2 = o1.p + np.array([np.cos(angle2), np.sin(angle2)]) * rel.o_distance
            
            line1, = self.ax.plot([o1.p[0], cone1[0]], [o1.p[1], cone1[1]], 'k--', linewidth=0.7, zorder=self.zorder)
            self.line1_graphs[rel.name] = line1
            
            line2, = self.ax.plot([o1.p[0], cone2[0]], [o1.p[1], cone2[1]], 'k--', linewidth=0.7, zorder=self.zorder)   
            self.line2_graphs[rel.name] = line2 
            self.graphs += [vo_circle, line1, line2]
            
            
    def do_update(self, new_env : LogicalScenario) -> List[plt.Artist]:
        for rel in new_env.relations:
            if rel.vessel2.is_OS():
                o1 = rel.vessel2
                o2 = rel.vessel1
                p12 = rel.p21
            else:
                o1 = rel.vessel1
                o2 = rel.vessel2
                p12 = rel.p12
            
            self.circle_graphs[rel.name].set_center(o2.p)
            self.circle_graphs[rel.name].set_radius(rel.safety_dist)
            # Calculate the angles of the cone
            # Calculate the angles of the cone
            angle_rel = np.arctan2(p12[1], p12[0])
            
            # Calculate the angles of the cone
            angle_rel = np.arctan2(p12[1], p12[0])
            sin_half_cone_theta = np.clip(rel.safety_dist / rel.o_distance, -1, 1)
            angle_half_cone = abs(np.arcsin(sin_half_cone_theta)) # [0, pi/2] 
            angle1 = angle_rel + angle_half_cone
            angle2 = angle_rel - angle_half_cone
            
            # Plot the velocity obstacle cone
            cone1 = o1.p + np.array([np.cos(angle1), np.sin(angle1)]) * rel.o_distance
            cone2 = o1.p + np.array([np.cos(angle2), np.sin(angle2)]) * rel.o_distance
            
            self.line1_graphs[rel.name].set_data([o1.p[0], cone1[0]], [o1.p[1], cone1[1]])
            self.line2_graphs[rel.name].set_data([o1.p[0], cone2[0]], [o1.p[1], cone2[1]])
        return self.graphs