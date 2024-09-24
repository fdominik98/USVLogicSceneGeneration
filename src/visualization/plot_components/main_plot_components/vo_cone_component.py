from typing import Dict, List
from matplotlib import pyplot as plt
import numpy as np
from model.environment.usv_environment import USVEnvironment
from visualization.plot_components.plot_component import PlotComponent, colors


class VOConeComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, env : USVEnvironment) -> None:
        super().__init__(ax, env)
        self.other_velocity_graphs : Dict[str, plt.Quiver] = {}
        self.line1_graphs : Dict[str, plt.Line2D] = {}
        self.line2_graphs : Dict[str, plt.Line2D] = {}
        self.filling_graphs : Dict[str, plt.Polygon] = {}
        self.graphs_by_colregs = [self.other_velocity_graphs, self.line1_graphs, self.line2_graphs, self.filling_graphs]
        self.zorder = -1
            
    def do_draw(self):
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
        
            line1, = self.ax.plot([o2.v[0] + o1.p[0], cone1[0]], [o2.v[1] + o1.p[1], cone1[1]], '--', color=colors[o2.id], linewidth=0.7, zorder=self.zorder)
            line2, = self.ax.plot([o2.v[0] + o1.p[0], cone2[0]], [o2.v[1] + o1.p[1], cone2[1]], '--', color=colors[o2.id], linewidth=0.7, zorder=self.zorder)
            self.line1_graphs[colreg_s.name] = line1
            self.line2_graphs[colreg_s.name] = line2
        
            # Move the other vessels velocity vector in the o1 position to see if the vector is in the VO cone  
            other_velocity = self.ax.quiver(o1.p[0], o1.p[1], o2.v[0], o2.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o2.id], zorder=self.zorder-10)
            self.other_velocity_graphs[colreg_s.name] = other_velocity
            
            # Fill the cone with a semi-transparent color
            filling = self.ax.fill([o2.v[0] + o1.p[0], cone1[0], cone2[0]],
                        [o2.v[1] + o1.p[1], cone1[1], cone2[1]],
                        color=colors[o2.id], alpha=0.15, zorder=self.zorder)
            self.filling_graphs[colreg_s.name] = filling[0]
            
            self.graphs += [line1, line2, other_velocity, filling[0]] 
        
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        for colreg_s in new_env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2
            # Calculate the angles of the cone
            angle_rel = np.arctan2(colreg_s.p12[1], colreg_s.p12[0])
            angle1 = angle_rel + colreg_s.angle_half_cone
            angle2 = angle_rel - colreg_s.angle_half_cone
            
            cone_size = max(colreg_s.o_distance / 2, (o1.speed + o2.speed) * 1.2)
                        
            cone1 = o2.v + o1.p + np.array([np.cos(angle1), np.sin(angle1)]) * cone_size
            cone2 = o2.v + o1.p + np.array([np.cos(angle2), np.sin(angle2)]) * cone_size
            self.line1_graphs[colreg_s.name].set_data([o2.v[0] + o1.p[0], cone1[0]], [o2.v[1] + o1.p[1], cone1[1]])
            self.line2_graphs[colreg_s.name].set_data([o2.v[0] + o1.p[0], cone2[0]], [o2.v[1] + o1.p[1], cone2[1]])
            self.other_velocity_graphs[colreg_s.name].set_offsets(o1.p)
            self.other_velocity_graphs[colreg_s.name].set_UVC(o2.v[0], o2.v[1])
            
            polx = [o2.v[0] + o1.p[0], cone1[0], cone2[0]]
            poly = [o2.v[1] + o1.p[1], cone1[1], cone2[1]]
            self.filling_graphs[colreg_s.name].set_xy(np.array([polx, poly]).T)
        return self.graphs