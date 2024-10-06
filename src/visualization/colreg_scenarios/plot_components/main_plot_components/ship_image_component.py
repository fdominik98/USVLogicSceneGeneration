from typing import Dict, List
from matplotlib import pyplot as plt
import numpy as np
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_config import ASSET_FOLDER
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, light_colors
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from scipy.ndimage import rotate
import matplotlib.image as mpimg

class ShipImageComponent(PlotComponent):
    ZOOM = 0.3
    img_dir = f'{ASSET_FOLDER}/images'
    
    def __init__(self, ax: plt.Axes, env : USVEnvironment) -> None:
        super().__init__(ax, env)
        self.image = mpimg.imread(f'{self.img_dir}/ship2.png')
        self.ship_image_graphs : List[AnnotationBbox] = []
        self.ship_offset_images : List[OffsetImage] = []
        self.traj_line_graphs : List[plt.Line2D] = []
        self.xs : Dict[int, List[float]] = {o.id : [] for o in env.vessels}
        self.ys : Dict[int, List[float]] = {o.id : [] for o in env.vessels}
        self.zorder = -4
        
    def do_draw(self):
        for o in self.env.vessels:
            (line,) = self.ax.plot([], [], ':', lw=3, color=light_colors[o.id], zorder=self.zorder-10)
            self.traj_line_graphs.append(line)
            
            # Rotate and plot image
            rotated_image = np.clip(rotate(self.image, np.degrees(o.heading)-90, reshape=True), 0, 1)
            image_box = OffsetImage(rotated_image, zoom = self.ZOOM, alpha=0.9)
            ab = AnnotationBbox(image_box, o.p, xybox= o.p, xycoords='data', frameon = False, zorder=self.zorder)
            self.ax.add_artist(ab)
            self.ship_image_graphs.append(ab)
            self.ship_offset_images.append(image_box)
            
            self.graphs += [line, ab]
            
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        for o in new_env.vessels:
            xs = self.xs[o.id]
            ys = self.ys[o.id]
            if o.p[0] not in xs or o.p[1] not in ys:
                xs.append(o.p[0])
                ys.append(o.p[1])
                
            self.traj_line_graphs[o.id].set_data(self.xs[o.id], self.ys[o.id])
            
            rotated_image = np.clip(rotate(self.image, np.degrees(o.heading)-90, reshape=True), 0, 1)
            
            self.ship_offset_images[o.id].set_data(rotated_image)
            self.ship_image_graphs[o.id].xybox = (o.p[0], o.p[1])
            self.ship_image_graphs[o.id].xy = (o.p[0], o.p[1])
        return self.graphs
    
    