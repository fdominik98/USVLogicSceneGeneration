from typing import List
from matplotlib import pyplot as plt
import numpy as np
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_config import KNOT_TO_MS_CONVERSION
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors


class ShipMarkingsComponent(PlotComponent):
    STATIC_ZOOM = 100
    DYNAMIC_ZOOM = 50
    def __init__(self, ax: plt.Axes, env : USVEnvironment) -> None:
        super().__init__(ax, env)
        self.radius_graphs : List[plt.Circle] = []
        self.velocity_graphs : List[plt.Quiver] = []
        self.ship_dot_graphs : List[plt.PathCollection] = []
        self.zorder = 0
        
            
    def do_draw(self):
        for o in self.env.vessels:
            #Plot the positions and radius as circles
            radius_circle = plt.Circle(o.p, o.r, color=colors[o.id], fill=False, linestyle='--', zorder=self.zorder)
            self.ax.add_artist(radius_circle)
            self.radius_graphs.append(radius_circle)

            # Plot the positions
            dot_label = f'{o}\; p: ({o.p[0]:.1f}, {o.p[1]:.1f}), r: {o.r:.1f} m'
            ship_dot = self.ax.scatter(o.p[0], o.p[1], color=colors[o.id], s=self.DYNAMIC_ZOOM, label=rf'${dot_label}$', zorder=self.zorder)
            self.ship_dot_graphs.append(ship_dot)
            
            angle = f'h: {np.degrees(o.heading):.1f}^\circ'
            speed = f'sp: {(o.speed / KNOT_TO_MS_CONVERSION):.1f} kn'
            velocity_label =f'{o}\; {angle}, {speed}'
            # Plot the velocity vector with their actual lengths
            ship_vel = self.ax.quiver(o.p[0], o.p[1], o.v[0], o.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o.id], label=rf'${velocity_label}$', zorder=self.zorder-10)
            self.velocity_graphs.append(ship_vel)
            
            
            self.graphs += [radius_circle, ship_vel, ship_dot]
        
                     
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        for o in new_env.vessels:
            self.radius_graphs[o.id].set_center(o.p)
            self.radius_graphs[o.id].set_radius(o.r)            
            self.ship_dot_graphs[o.id].set_offsets([o.p])  
            self.velocity_graphs[o.id].set_offsets(o.p)
            self.velocity_graphs[o.id].set_UVC(o.v[0], o.v[1])
        return self.graphs
            
    