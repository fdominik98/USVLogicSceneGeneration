from typing import Dict, List
from matplotlib import pyplot as plt
import numpy as np
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
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
        self.image = mpimg.imread(f'{self.img_dir}/ship2.png')
        self.ship_image_graphs : Dict[ConcreteVessel, AnnotationBbox] = {}
        self.ship_offset_images : Dict[ConcreteVessel, OffsetImage] = {}
        self.traj_line_graphs : Dict[ConcreteVessel, plt.Line2D] = {}
        self.xs : Dict[ConcreteVessel, List[float]] = {vessel : [] for vessel in scenario.concrete_scene.actors}
        self.ys : Dict[ConcreteVessel, List[float]] = {vessel : [] for vessel in scenario.concrete_scene.actors}
        self.zorder = -4
        
    def do_draw(self):
        for vessel, state in self.scenario.concrete_scene.items():         
            zoom = 0.32 + vessel.length / MAX_LENGTH / 10
            (line,) = self.ax.plot(self.xs[vessel], self.ys[vessel], ':', lw=3, color=light_colors[vessel.id], zorder=self.zorder-10)
            self.traj_line_graphs[vessel] = line
            
            # Rotate and plot image
            rotated_image = np.clip(rotate(self.image, np.degrees(state.heading)-90, reshape=True), 0, 1)
            image_box = OffsetImage(rotated_image, zoom = zoom, alpha=1)
            ab = AnnotationBbox(image_box, state.p, xybox= state.p, xycoords='data', frameon = False, zorder=self.zorder)
            self.ax.add_artist(ab)
            self.ship_image_graphs[vessel] = ab
            self.ship_offset_images[vessel] = image_box
            
            self.graphs += [line, ab]
            
    def do_update(self, scene : ConcreteScene) -> List[plt.Artist]:
        for vessel, state in scene.items():
            xs = self.xs[vessel]
            ys = self.ys[vessel]
            if state.x not in xs or state.y not in ys:
                xs.append(state.x)
                ys.append(state.y)                

            self.traj_line_graphs[vessel].set_data(xs, ys)
            
            rotated_image = np.clip(rotate(self.image, np.degrees(state.heading)-90, reshape=True), 0, 1)
            
            self.ship_offset_images[vessel].set_data(rotated_image)
            self.ship_image_graphs[vessel].xybox = (state.x, state.y)
            self.ship_image_graphs[vessel].xy = (state.x, state.y)
        return self.graphs
    
    