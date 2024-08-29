from matplotlib import pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import KNOT_TO_MS_CONVERSION
from visualization.plot_component import PlotComponent, colors


class ShipMarkingsComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)
        self.radius_visibility = True
        self.radius_graphs : list[plt.Artist] = []
            
    def do_draw(self, zorder : int):
        for o in self.env.vessels:
            #self.ax.text(o.p[0] + o.r*1.5, o.p[1] + o.r*1.5, f'O{o.id}: ({o.p[0]:.2f}, {o.p[1]:.2f})\nv{o.id} speed: {o.speed:.2f} m/s', fontsize=11, color=colors[o.id], fontweight='bold')
            #name_text = self.ax.text(o.p[0] + o.l, o.p[1] + o.l, name, color=colors[o.id], fontweight='bold', zorder=zorder)
            
            #Plot the positions and radius as circles
            radius_circle = plt.Circle(o.p, o.l, color=colors[o.id], fill=False, linestyle='--', label=f'{o.name} Radius: {o.l}m', zorder=zorder)
            self.ax.add_artist(radius_circle)
            self.radius_graphs.append(radius_circle)

            angle = fr'$\theta = {np.degrees(o.heading):.2f}^\circ$'
            speed = f'speed = {(o.speed / KNOT_TO_MS_CONVERSION):.2f}kn'
            # Plot the velocity vector with their actual lengths
            ship_vel = self.ax.quiver(o.p[0], o.p[1], o.v[0], o.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o.id], label=f'{o.name} Velocity: {angle}, {speed}', zorder=zorder-10)

            # Plot the positions
            ship_dot = self.ax.scatter(o.p[0], o.p[1], color=colors[o.id], s=100, label=f'{o.name} Position: ({o.p[0]:.2f}, {o.p[1]:.2f})', zorder=zorder)
            
            #self.graphs += [name_text, radius_circle, ship_vel, ship_dot]
            self.graphs += [ship_vel, ship_dot]
        self.refresh_radius_graphs()
        
    def toggle(self):
        if self.visible and self.radius_visibility:
            self.radius_visibility = False
        elif self.visible and not self.radius_visibility:
            self.visible = False
        else:
            self.visible = True
            self.radius_visibility = True
        self.refresh_radius_graphs()
        self.refresh_visible()
        
    def refresh_radius_graphs(self):
        for g in self.radius_graphs:
            g.set_visible(self.radius_visibility)