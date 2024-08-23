import matplotlib.pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import *
import os
from model.colreg_situation import NoColreg
import matplotlib.image as mpimg
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from scipy.ndimage import rotate
from visualization.detailed_angle_circle_component import DetailedAngleCircleComponent
from visualization.ship_markings_component import ShipMarkingsComponent
from visualization.angle_circle_component import AngleCircleComponent
from visualization.distance_component import DistanceComponent
from visualization.vo_cone_component import VOConeComponent
from visualization.additional_vo_cone_component import AdditionalVOConeComponent

import matplotlib.gridspec as gridspec

script_path = os.path.abspath(__file__)
current_dir = os.path.dirname(script_path)
img_dir = f'{current_dir}/../../assets/images'

class ColregPlot():  
    
    def __init__(self, env : USVEnvironment): 
        self.env = env
        self.gs = gridspec.GridSpec(1, 2, width_ratios=[1, 0])
        self.fig = plt.figure(figsize=(10,10)) 
        self.ax = self.fig.add_subplot(self.gs[0])
        self.lax = self.fig.add_subplot(self.gs[1])
           
        self.legend_visible = True
        self.axis_visible = True
        
        self.vo_cone_component = VOConeComponent(self.ax, False, self.env)
        self.additional_vo_cone_component = AdditionalVOConeComponent(self.ax, False, self.env)
        self.distance_component = DistanceComponent(self.ax, True, self.env)
        self.angle_circle_component = AngleCircleComponent(self.ax, True, self.env, linewidth=2.0)
        self.detailed_angle_circle_component = DetailedAngleCircleComponent(self.ax, True, self.env)
        self.ship_markings_component = ShipMarkingsComponent(self.ax, True, self.env)
        
        
        self.image = mpimg.imread(f'{img_dir}/ship2.png')
        #self.image = self.convert_non_white_to_gray(self.image)
        
        self.draw()   
        
    def draw(self):
        # Create the plot            
        self.title = ''
        i = 0
        self.min_distances : dict[int, float]= {}
        
        self.ship_markings_component.draw(0)
        self.vo_cone_component.draw(-1)
        self.additional_vo_cone_component.draw(-2)
        self.distance_component.draw(-3)
        self.angle_circle_component.draw(-4)
        self.detailed_angle_circle_component.draw(-4)
        
        for colreg_s in self.env.colreg_situations:
            if not isinstance(colreg_s, NoColreg): 
                line_break = '\n' if (i + 1) % 3 == 0 else ' '
                self.title = colreg_s.name if not self.title else f'{self.title},{line_break}{colreg_s.name}'
                i += 1
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2
            
            if o1.id not in self.min_distances or self.min_distances[o1.id] > colreg_s.o_distance:
                self.min_distances[o1.id] = colreg_s.o_distance
            if o2.id not in self.min_distances or self.min_distances[o2.id] > colreg_s.o_distance:
                self.min_distances[o2.id] = colreg_s.o_distance
            
            colreg_s.info()            
            
        for o in self.env.vessels:
            # Rotate and plot image
            rotated_image = rotate(self.image, np.degrees(o.heading)-90, reshape=True)
            imagebox = OffsetImage(rotated_image, zoom = 0.35, alpha=0.9)
            ab = AnnotationBbox(imagebox, o.p, frameon = False, zorder=-4)
            self.ax.add_artist(ab)
                        
        self.set_layout()        

        # Connect the key press event to the toggle function
        self.fig.canvas.mpl_connect('key_press_event', lambda e: self.toggle_visibility(e))

        plt.show(block=True)
        
    def set_layout(self):
        self.fig.tight_layout(pad=5)
        self.ax.grid(False)
        h, l = self.ax.get_legend_handles_labels()
        self.lax.legend(h, l, loc=7)
        self.lax.axis("off")

        self.ax.set_title(f'USV situation ({self.title})')
        self.ax.set_xlabel('X Position (m)')
        self.ax.set_ylabel('Y Position (m)')
        self.ax.set_aspect('equal', adjustable='box')                  
           
        # Recalculate the limits based on the current data     
        self.ax.relim()

        # Automatically adjust xlim and ylim
        self.ax.autoscale_view()
        # Get current x and y limits
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
        # Define a padding percentage (e.g., 5% of the range)
        x_padding = (x_max - x_min) * 0.02
        y_padding = (y_max - y_min) * 0.02
        # Set new limits with padding applied
        self.ax.set_xlim(x_min - x_padding, x_max + x_padding)
        self.ax.set_ylim(y_min - y_padding, y_max + y_padding)
        
        
    # Function to toggle the visibility
    def toggle_visibility(self, event):
        if event.key == '0':
            self.legend_visible = not self.legend_visible
            self.lax.set_visible(self.legend_visible)
        elif event.key == '1':
            self.distance_component.toggle()
        elif event.key == '2':
            self.vo_cone_component.toggle()
        elif event.key == '3':
            self.additional_vo_cone_component.toggle()
        elif event.key == '4':
            self.axis_visible = not self.axis_visible
            self.ax.axis(self.axis_visible)
            self.ax.title.set_visible(self.axis_visible)
        elif event.key == '5':
            self.ship_markings_component.toggle()
        elif event.key == '6':
            self.angle_circle_component.toggle()
        elif event.key == '7':
            self.detailed_angle_circle_component.toggle()
        self.fig.canvas.draw()    
        
        
    def convert_non_white_to_gray(self, image, alpha=255):
        # Create a copy of the image to modify
        gray_image = image.copy()
        
        # Define the gray color with an alpha channel
        gray_color = np.array([128, 128, 128, alpha])  # RGBA value for gray (255 is full opacity)
        
        # Identify non-white pixels (assuming white is [255, 255, 255, 255] in RGBA)
        non_white_pixels = np.all(image[:, :, :3] != [255, 255, 255], axis=-1)
        
        # Assign gray color to non-white pixels, preserving the alpha channel
        gray_image[non_white_pixels, :3] = gray_color[:3]
        # Optionally, you can set the alpha channel to a specific value as well
        gray_image[non_white_pixels, 3] = gray_color[3]
        return gray_image
        
                