from matplotlib import pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import KNOT_TO_MS_CONVERSION
from visualization.plot_component import PlotComponent, colors


class ShipMarkingsComponent(PlotComponent):
    STATIC_ZOOM = 100
    DYNAMIC_ZOOM = 50
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)
        self.radius_visibility = True
        self.markings_visibility = initial_visibility
        self.radius_graphs : list[plt.Circle] = []
        self.velocity_graphs : list[plt.Quiver] = []
        self.ship_dot_graphs : list[plt.PathCollection] = []
        
            
    def do_draw(self, zorder : int):
        for o in self.env.vessels:
            #Plot the positions and radius as circles
            radius_circle = plt.Circle(o.p, o.r, color=colors[o.id], fill=False, linestyle='--', label=f'{o.name} Radius: {o.r}m', zorder=zorder)
            self.ax.add_artist(radius_circle)
            self.radius_graphs.append(radius_circle)

            angle = fr'$\theta = {np.degrees(o.heading):.2f}^\circ$'
            speed = f'speed = {(o.speed / KNOT_TO_MS_CONVERSION):.2f}kn'
            velocity_label =f'{o.name} Velocity: {angle}, {speed}'
            # Plot the velocity vector with their actual lengths
            ship_vel = self.ax.quiver(o.p[0], o.p[1], o.v[0], o.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o.id], label=velocity_label, zorder=zorder-10)
            self.velocity_graphs.append(ship_vel)
            
            # Plot the positions
            dot_label = f'{o.name} Position: ({o.p[0]:.2f}, {o.p[1]:.2f})'
            ship_dot = self.ax.scatter(o.p[0], o.p[1], color=colors[o.id], s=self.DYNAMIC_ZOOM, label=dot_label, zorder=zorder)
            self.ship_dot_graphs.append(ship_dot)
            #self.graphs += [name_text, radius_circle, ship_vel, ship_dot]
            self.graphs += [radius_circle, ship_vel, ship_dot]
        self.refresh_visible()
        
        
    def toggle(self):
        if self.markings_visibility and self.radius_visibility:
            self.radius_visibility = False
            self.visible = True
        elif self.markings_visibility and not self.radius_visibility:
            self.markings_visibility = False
            self.visible = False
        else:
            self.markings_visibility = True
            self.radius_visibility = True
            self.visible = True
        self.refresh_visible()
            
    def refresh_visible(self):
        for g in self.radius_graphs:
            g.set_visible(self.radius_visibility)
        for g in self.ship_dot_graphs:
            g.set_visible(self.markings_visibility)
        for g in self.velocity_graphs:
            g.set_visible(self.markings_visibility)
        
             
    def do_update(self, new_env : USVEnvironment) -> list[plt.Artist]:
        for o in new_env.vessels:
            self.radius_graphs[o.id].set_center(o.p)
            self.radius_graphs[o.id].set_radius(o.r)
            dot_label = f'{o.name} Position: ({o.p[0]:.2f}, {o.p[1]:.2f})'
            self.ship_dot_graphs[o.id].set_label(dot_label)
            self.ship_dot_graphs[o.id].set_offsets([o.p])
            
            angle = fr'$\theta = {np.degrees(o.heading):.2f}^\circ$'
            speed = f'speed = {(o.speed / KNOT_TO_MS_CONVERSION):.2f}kn'
            velocity_label =f'{o.name} Velocity: {angle}, {speed}'
            self.velocity_graphs[o.id].set_label(velocity_label)
            self.velocity_graphs[o.id].set_offsets(o.p)
            self.velocity_graphs[o.id].set_UVC(o.v[0], o.v[1])
        return self.graphs
            
    