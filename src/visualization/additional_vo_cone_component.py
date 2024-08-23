from matplotlib import pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent


class AdditionalVOConeComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)
            
    def do_draw(self, zorder : int):
        for colreg_s in self.env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2
            vo_circle = plt.Circle(o2.p, colreg_s.safety_dist, color='black', fill=False, linestyle='--', linewidth=0.7, zorder=zorder)
            self.ax.add_artist(vo_circle)
            # Calculate the angles of the cone
            angle_rel = np.arctan2(colreg_s.p12[1], colreg_s.p12[0])
            angle1 = angle_rel + colreg_s.angle_half_cone
            angle2 = angle_rel - colreg_s.angle_half_cone
            
            # Plot the velocity obstacle cone
            cone1 = o1.p + np.array([np.cos(angle1), np.sin(angle1)]) * colreg_s.o_distance
            cone2 = o1.p + np.array([np.cos(angle2), np.sin(angle2)]) * colreg_s.o_distance
            line1, = self.ax.plot([o1.p[0], cone1[0]], [o1.p[1], cone1[1]], 'k--', linewidth=0.7, zorder=zorder)
            line2, = self.ax.plot([o1.p[0], cone2[0]], [o1.p[1], cone2[1]], 'k--', linewidth=0.7, zorder=zorder)    
            self.graphs += [vo_circle, line1, line2]
            