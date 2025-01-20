from typing import Dict, List
from matplotlib import pyplot as plt
import numpy as np
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from utils.asv_utils import KNOT_TO_MS_CONVERSION
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors


class ShipMarkingsComponent(PlotComponent):
    STATIC_ZOOM = 100
    DYNAMIC_ZOOM = 50
    def __init__(self, ax : plt.Axes, scenario : MultiLevelScenario) -> None:
        super().__init__(ax, scenario)
        self.radius_graphs : Dict[ConcreteVessel, plt.Circle] = {}
        self.velocity_graphs : Dict[ConcreteVessel, plt.Quiver] = {}
        self.ship_dot_graphs : Dict[ConcreteVessel, plt.PathCollection] = {}
        self.zorder = 0
        
            
    def do_draw(self):
        for vessel, state in self.scenario.concrete_scene.items():
            #Plot the positions and radius as circles
            radius_circle = plt.Circle(state.p, vessel.radius, color=colors[vessel.id], fill=False, linestyle='--', zorder=self.zorder)
            self.ax.add_artist(radius_circle)
            self.radius_graphs[vessel] = radius_circle

            # Plot the positions
            dot_label = f'{vessel}\; p: ({state.p[0]:.1f}, {state.p[1]:.1f}), r: {vessel.radius:.1f} m'
            ship_dot = self.ax.scatter(state.p[0], state.p[1], color=colors[vessel.id], s=self.DYNAMIC_ZOOM, label=rf'${dot_label}$', zorder=self.zorder)
            self.ship_dot_graphs[vessel] = ship_dot
            
            angle = f'h: {np.degrees(state.heading):.1f}^\circ'
            speed = f'sp: {(state.speed / KNOT_TO_MS_CONVERSION):.1f} kn'
            velocity_label = f'{vessel}\; {angle}, {speed}'
            # Plot the velocity vector with their actual lengths
            ship_vel = self.ax.quiver(state.p[0], state.p[1], state.v[0], state.v[1], angles='xy', scale_units='xy', scale=1, color=colors[vessel.id], label=rf'${velocity_label}$', zorder=self.zorder-10)
            self.velocity_graphs[vessel] = ship_vel
            
            
            self.graphs += [radius_circle, ship_vel, ship_dot]
        
                     
    def do_update(self, scene : ConcreteScene) -> List[plt.Artist]:
        for vessel, state in scene.items():
            self.radius_graphs[vessel].set_center(state.p)
            self.radius_graphs[vessel].set_radius(vessel.radius)            
            self.ship_dot_graphs[vessel].set_offsets([state.p])  
            self.velocity_graphs[vessel].set_offsets(state.p)
            self.velocity_graphs[vessel].set_UVC(state.v[0], state.v[1])
        return self.graphs
            
    