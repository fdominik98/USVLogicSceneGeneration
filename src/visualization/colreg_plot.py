from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from model.usv_environment import USVEnvironment
from model.usv_config import *
from model.colreg_situation import NoColreg
from aggregates import VesselAggregate
from visualization.drawing_component import DrawingComponent
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
        self.trajectories = trajectories
        self.block = block
        self.axis_visible = True
        self.create_fig()
        
        self.components : Dict[str, PlotComponent] = {
            '5' : ShipMarkingsComponent(self.ax, True, self.env),
            'drawing' : DrawingComponent(self.fig, self.ax, True, self.env),
            '0' : LegendComponent(self.ax, True, self.env),
        }
        self.configure()
        
           
        self.animation = ColregAnimation(self.fig, self.env, self.components.values(), trajectories)
        
        self.draw()   
        
        # Connect the key press event to the toggle function
        self.fig.canvas.mpl_connect('key_press_event', lambda e: self.toggle_visibility(e))
        self.fig.canvas.mpl_connect('key_press_event', lambda e: self.animation.toggle_anim(e))
        # Connect the click and move events to their handlers
        drawing_component : DrawingComponent = self.components['drawing']
        self.fig.canvas.mpl_connect('button_press_event', drawing_component.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', drawing_component.on_move)
        
        plt.show(block=self.block)
     
        
    def create_fig(self):
        fig, ax = plt.subplots(1, 1, figsize=(10, 10), gridspec_kw={'width_ratios': [1]})
        self.fig : plt.Figure = fig
        self.ax : plt.Axes = ax
     
    def configure(self):
        self.components |= {
            '2' : VOConeComponent(self.ax, False, self.env),
            '3' : AdditionalVOConeComponent(self.ax, False, self.env),
            '1' : DistanceComponent(self.ax, True, self.env),
            '6' : AngleCircleComponent(self.ax, True, self.env, linewidth=1.5),
            #'7' : CenteredAngleCircleComponent(self.ax, True, self.env, center_vessel_id=0),            
            '8' : PrimeComponent(self.ax, False, self.env),
            '9' : ShipImageComponent(self.ax, True, self.env)                   
        }
           
    # Function to toggle the visibility
    def toggle_visibility(self, event):
        if event.key == '4':
            self.axis_visible = not self.axis_visible
            self.ax.axis(self.axis_visible)
            self.ax.title.set_visible(self.axis_visible)
        else:
            for id, comp in self.components.items():
                if event.key == id:
                    comp.toggle()
        self.fig.canvas.draw()    
        
        
    def draw(self):
        for component in self.components.values():
            component.draw()
        
        self.title = ''
        columns = 0
        for colreg_s in self.env.colreg_situations:
            if not isinstance(colreg_s, NoColreg): 
                line_break = '\n' if (columns + 1) % 3 == 0 else ' '
                self.title = colreg_s.name if not self.title else f'{self.title},{line_break}{colreg_s.name}'
                columns += 1
            colreg_s.info() 
            
        vessel_aggr = VesselAggregate(env=self.env, minimize=True)
        print(f'Loost penalty: {vessel_aggr.loose_evaluate()}, strict penalty: {vessel_aggr.strict_evaluate()}')                      
                        
        self.set_layout()    
        
        
    def set_layout(self):
        self.fig.subplots_adjust(bottom=0.35)
        #self.fig.tight_layout(pad=10)
        self.ax.grid(False)
       
        self.ax.set_title(f'USV situation ({self.title})')
        self.ax.set_xlabel('X Position (m)')
        self.ax.set_ylabel('Y Position (m)')
        self.ax.set_aspect('equal', adjustable='box')      
        
        # Recalculate the limits based on the current data     
        self.ax.relim()
        # Automatically adjust xlim and ylim
        #self.ax.autoscale_view()
        self.ax.margins(x=0.2, y=0.2)
        # # Get current x and y limits
        # x_min, x_max = self.ax.get_xlim()
        # y_min, y_max = self.ax.get_ylim()
        # # Define a padding percentage (e.g., 5% of the range)
        # x_padding = (x_max - x_min) * 0.03
        # y_padding = (y_max - y_min) * 0.03
        # # Set new limits with padding applied
        # self.ax.set_xlim(x_min + x_padding, x_max - x_padding)
        # self.ax.set_ylim(y_min + y_padding, y_max - y_padding)      
           
        
        
        

    