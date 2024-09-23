from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib
from model.usv_environment import USVEnvironment
from model.usv_config import *
from model.colreg_situation import NoColreg
from aggregates import VesselAggregate
from trajectory_planning.path_interpolator import PathInterpolator
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

class TrajectoryReceiver():
    def __init__(self, env : USVEnvironment, trajectories : Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None) -> None:
        self.env = env
        self.trajectories = trajectories
        if self.trajectories is None:
            interpolator = PathInterpolator()
            for v in env.vessels:
                interpolator.add_path(v, [])
            self.trajectories = interpolator.interpolated_paths

class ColregPlot(TrajectoryReceiver):  
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['font.size'] = 12
    
    def __init__(self, env : USVEnvironment, 
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None): 
        super().__init__(env, trajectories)
            
        self.create_fig()
        
        self.ship_markings_component = ShipMarkingsComponent(self.ax, self.env)
        self.drawing_component = DrawingComponent(self.fig, self.ax, self.env)
        self.legend_component = LegendComponent(self.ax, self.env)
        self.vo_cone_component = VOConeComponent(self.ax, self.env)
        self.add_vo_cone_component = AdditionalVOConeComponent(self.ax, self.env)
        self.distance_component = DistanceComponent(self.ax, self.env)
        self.angle_circle_component = AngleCircleComponent(self.ax, self.env, linewidth=1.5)
        self.centered_angle_circle_component = CenteredAngleCircleComponent(self.ax, self.env)          
        self.prime_component = PrimeComponent(self.ax, self.env)
        self.ship_image_component = ShipImageComponent(self.ax, self.env)    
        
        self.components : List[PlotComponent] = [
            self.ship_markings_component,
            self.drawing_component,
            self.legend_component,
            self.vo_cone_component,
            self.add_vo_cone_component,
            self.distance_component,
            self.angle_circle_component,
            self.centered_angle_circle_component,
            self.prime_component,
            self.ship_image_component
        ]
        
        self.draw()  
         
        self.animation = ColregAnimation(self.fig, self.env, self.components, self.trajectories)
        
        # Connect the key press event to the toggle function
        self.fig.canvas.mpl_connect('key_press_event', lambda e: self.animation.toggle_anim(e))
        # Connect the click and move events to their handlers
        self.fig.canvas.mpl_connect('button_press_event', self.drawing_component.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.drawing_component.on_move)
        
        
    def create_fig(self):
        fig, ax = plt.subplots(1, 1, gridspec_kw={'width_ratios': [1]})
        self.fig : plt.Figure = fig
        self.ax : plt.Axes = ax     

        
    def draw(self):
        for component in self.components:
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
        print(f'Loose penalty: {vessel_aggr.loose_evaluate()}, strict penalty: {vessel_aggr.strict_evaluate()}')                      
                        
        self.set_layout()    
        
        
    def set_layout(self):
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
        # # Get current x and y limits
        # x_min, x_max = self.ax.get_xlim()
        # y_min, y_max = self.ax.get_ylim()
        # # Define a padding percentage (e.g., 5% of the range)
        # x_padding = (x_max - x_min) * 0.03
        # y_padding = (y_max - y_min) * 0.03
        # # Set new limits with padding applied
        # self.ax.set_xlim(x_min + x_padding, x_max - x_padding)
        # self.ax.set_ylim(y_min + y_padding, y_max - y_padding)      
           
        
        
        

    