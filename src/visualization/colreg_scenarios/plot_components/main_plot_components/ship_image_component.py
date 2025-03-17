from typing import Dict, List
from matplotlib import pyplot as plt
import numpy as np
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_actors import ConcreteActor
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from utils.asv_utils import MAX_LENGTH
from utils.file_system_utils import ASSET_FOLDER
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, light_colors
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from scipy.ndimage import rotate
import matplotlib.image as mpimg

class ShipImageComponent(PlotComponent):
    img_dir = f'{ASSET_FOLDER}/images'
    
    def __init__(self, ax : plt.Axes, scenario : MultiLevelScenario) -> None:
        super().__init__(ax, scenario)
        self.ship_image = mpimg.imread(f'{self.img_dir}/ship.png')
        self.buoy_image = mpimg.imread(f'{self.img_dir}/buoy.png')
        self.image_graphs : Dict[ConcreteActor, AnnotationBbox] = {}
        self.offset_images : Dict[ConcreteActor, OffsetImage] = {}
        self.traj_line_graphs : Dict[ConcreteActor, plt.Line2D] = {}
        self.xs : Dict[ConcreteActor, List[float]] = {actor : [] for actor in scenario.concrete_scene.actors}
        self.ys : Dict[ConcreteActor, List[float]] = {actor : [] for actor in scenario.concrete_scene.actors}
        self.zorder = -4
        
    def do_draw(self):
        for actor, state in self.scenario.concrete_scene.items():         
            zoom = 0.32 + actor.radius / MAX_LENGTH / 40
            (line,) = self.ax.plot(self.xs[actor], self.ys[actor], ':', lw=3, color=light_colors[actor.id], zorder=self.zorder-10)
            self.traj_line_graphs[actor] = line
            
            # Rotate and plot image
            rotated_image = np.clip(rotate(self.ship_image if actor.is_vessel else self.buoy_image,
                                           np.degrees(state.heading)-90, reshape=True), 0, 1)
            image_box = OffsetImage(rotated_image, zoom = zoom, alpha=1)
            ab = AnnotationBbox(image_box, state.p, xybox= state.p, xycoords='data', frameon = False, zorder=self.zorder)
            self.ax.add_artist(ab)
            self.image_graphs[actor] = ab
            self.offset_images[actor] = image_box
            
            self.graphs += [line, ab]
            
    def do_update(self, scene : ConcreteScene) -> List[plt.Artist]:
        for actor, state in scene.items():
            xs = self.xs[actor]
            ys = self.ys[actor]
            if state.x not in xs or state.y not in ys:
                xs.append(state.x)
                ys.append(state.y)                

            self.traj_line_graphs[actor].set_data(xs, ys)
            
            rotated_image = np.clip(rotate(self.ship_image if actor.is_vessel else self.buoy_image,
                                           np.degrees(state.heading)-90, reshape=True), 0, 1)
            
            self.offset_images[actor].set_data(rotated_image)
            self.image_graphs[actor].xybox = (state.x, state.y)
            self.image_graphs[actor].xy = (state.x, state.y)
        return self.graphs
    
    