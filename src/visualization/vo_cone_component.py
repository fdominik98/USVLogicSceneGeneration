from matplotlib import pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent, colors


class VOConeComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)
            
    def do_draw(self, zorder : int):
        for colreg_s in self.env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2
            # Calculate the angles of the cone
            angle_rel = np.arctan2(colreg_s.p12[1], colreg_s.p12[0])
            angle1 = angle_rel + colreg_s.angle_half_cone
            angle2 = angle_rel - colreg_s.angle_half_cone
            
            cone_size = max(colreg_s.o_distance / 2, (o1.speed + o2.speed) * 1.2)
                        
            cone1 = o2.v + o1.p + np.array([np.cos(angle1), np.sin(angle1)]) * cone_size
            cone2 = o2.v + o1.p + np.array([np.cos(angle2), np.sin(angle2)]) * cone_size

        
            line1, = self.ax.plot([o2.v[0] + o1.p[0], cone1[0]], [o2.v[1] + o1.p[1], cone1[1]], '--', color=colors[o2.id], linewidth=0.7, zorder=zorder)
            line2, = self.ax.plot([o2.v[0] + o1.p[0], cone2[0]], [o2.v[1] + o1.p[1], cone2[1]], '--', color=colors[o2.id], linewidth=0.7, zorder=zorder)
        
            # Move the other vessels velocity vector in the o1 position to see if the vector is in the VO cone  
            other_velocity = self.ax.quiver(o1.p[0], o1.p[1], o2.v[0], o2.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o2.id], zorder=zorder-10)
            
            
            # Fill the cone with a semi-transparent color
            filling = self.ax.fill([o2.v[0] + o1.p[0], cone1[0], cone2[0]],
                        [o2.v[1] + o1.p[1], cone1[1], cone2[1]],
                        color=colors[o2.id], alpha=0.15, zorder=zorder)
            
            self.graphs += [line1, line2, filling[0], other_velocity] 
        