from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from model.usv_environment import USVEnvironment
from model.usv_config import *
from model.colreg_situation import NoColreg
from visualization.legend_component import LegendComponent
from visualization.colreg_animation import ColregAnimation
from visualization.ship_image_component import ShipImageComponent
from visualization.plot_component import PlotComponent
from visualization.prime_component import PrimeComponent
from visualization.centered_angle_circle_component import CenteredAngleCircleComponent
from visualization.ship_markings_component import ShipMarkingsComponent
from visualization.angle_circle_component import AngleCircleComponent
from visualization.distance_component import DistanceComponent
from visualization.vo_cone_component import VOConeComponent
from visualization.additional_vo_cone_component import AdditionalVOConeComponent

class ColregPlot():  
    def __init__(self, env : USVEnvironment, block=True, 
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None): 
        self.env = env        
        self.fig = plt.figure(figsize=(10,10)) 
        self.ax = self.fig.add_subplot()
           
        self.block = block
        self.axis_visible = True
        
        self.vo_cone_component = VOConeComponent(self.ax, False, self.env)
        self.additional_vo_cone_component = AdditionalVOConeComponent(self.ax, False, self.env)
        self.distance_component = DistanceComponent(self.ax, True, self.env)
        self.angle_circle_component = AngleCircleComponent(self.ax, True, self.env, linewidth=1.5)
        self.detailed_angle_circle_component = CenteredAngleCircleComponent(self.ax, True, self.env, center_vessel_id=0)
        self.ship_markings_component = ShipMarkingsComponent(self.ax, True, self.env)
        self.prime_component = PrimeComponent(self.ax, False, self.env)
        self.ship_image_component = ShipImageComponent(self.ax, True, self.env)
        self.legend_component = LegendComponent(self.ax, True, self.env)
        
        self.components : List[PlotComponent] = [
            self.vo_cone_component,
            self.additional_vo_cone_component,
            self.distance_component,
            self.angle_circle_component,
            #self.detailed_angle_circle_component,
            self.ship_markings_component,
            self.prime_component,
            self.ship_image_component,
            self.legend_component
        ]
        
        self.animation = ColregAnimation(self.fig, self.env, self.components, trajectories)
        
        self.draw()   
        
        # Connect the key press event to the toggle function
        self.fig.canvas.mpl_connect('key_press_event', lambda e: self.toggle_visibility(e))
        self.fig.canvas.mpl_connect('key_press_event', lambda e: self.animation.toggle_anim(e))
        
        plt.show(block=self.block)
        
        
    def draw(self):
        self.ship_markings_component.draw(0)
        self.vo_cone_component.draw(-1)
        self.additional_vo_cone_component.draw(-2)
        self.distance_component.draw(-3)
        self.angle_circle_component.draw(-20)
        #self.detailed_angle_circle_component.draw(-20)
        self.prime_component.draw(-5)
        self.ship_image_component.draw(-4)
        self.legend_component.draw(0)
        
        self.title = ''
        i = 0
        for colreg_s in self.env.colreg_situations:
            if not isinstance(colreg_s, NoColreg): 
                line_break = '\n' if (i + 1) % 3 == 0 else ' '
                self.title = colreg_s.name if not self.title else f'{self.title},{line_break}{colreg_s.name}'
                i += 1
            colreg_s.info()                       
                        
        self.set_layout()    
        
        
    def set_layout(self):
        #self.fig.subplots_adjust(bottom=0.25)
        #self.fig.tight_layout(pad=5)
        self.ax.grid(False)
       
        self.ax.set_title(f'USV situation ({self.title})')
        self.ax.set_xlabel('X Position (m)')
        self.ax.set_ylabel('Y Position (m)')
        self.ax.set_aspect('equal', adjustable='box')      
        
        # Recalculate the limits based on the current data     
        self.ax.relim()
        # Automatically adjust xlim and ylim
        self.ax.autoscale_view(tight=True)
        # # Get current x and y limits
        # x_min, x_max = self.ax.get_xlim()
        # y_min, y_max = self.ax.get_ylim()
        # # Define a padding percentage (e.g., 5% of the range)
        # x_padding = (x_max - x_min) * 0.03
        # y_padding = (y_max - y_min) * 0.03
        # # Set new limits with padding applied
        # self.ax.set_xlim(x_min + x_padding, x_max - x_padding)
        # self.ax.set_ylim(y_min + y_padding, y_max - y_padding)      
           
        
        
    # Function to toggle the visibility
    def toggle_visibility(self, event):
        if event.key == '0':
            self.legend_component.toggle()
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
        elif event.key == '8':
            self.prime_component.toggle()
        elif event.key == '9':
            self.ship_image_component.toggle()
        self.fig.canvas.draw()    
        