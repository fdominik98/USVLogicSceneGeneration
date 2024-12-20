from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from logical_level.models.logical_scenario import LogicalScenario
from asv_utils import *
from logical_level.constraint_satisfaction.evolutionary_computation.aggregates import AggregateAll
from visualization.my_plot import MyPlot
from concrete_level.trajectory_generation.path_interpolator import PathInterpolator
from visualization.colreg_scenarios.plot_components.main_plot_components.drawing_component import DrawingComponent
from visualization.colreg_scenarios.plot_components.main_plot_components.legend_component import LegendComponent
from visualization.colreg_scenarios.colreg_animation import ColregAnimation
from visualization.colreg_scenarios.plot_components.main_plot_components.ship_image_component import ShipImageComponent
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent
from visualization.colreg_scenarios.plot_components.main_plot_components.prime_component import PrimeComponent
from visualization.colreg_scenarios.plot_components.main_plot_components.centered_angle_circle_component import CenteredAngleCircleComponent
from visualization.colreg_scenarios.plot_components.main_plot_components.ship_markings_component import ShipMarkingsComponent
from visualization.colreg_scenarios.plot_components.main_plot_components.angle_circle_component import AngleCircleComponent
from visualization.colreg_scenarios.plot_components.main_plot_components.distance_component import DistanceComponent
from visualization.colreg_scenarios.plot_components.main_plot_components.vo_cone_component import VOConeComponent
from visualization.colreg_scenarios.plot_components.main_plot_components.additional_vo_cone_component import AdditionalVOConeComponent

class TrajectoryReceiver():
    def __init__(self,logical_scenario: LogicalScenario, trajectories : Optional[Dict[int, List[Tuple[float, float, float, float, float]]]] = None) -> None:
        self.logical_scenario = env
        if trajectories is None:
            self.trajectories = self.gen_trajectories()
        else:
            self.trajectories = trajectories            
            
    def gen_trajectories(self):
        interpolator = PathInterpolator()
        for v in self.logical_scenario.vessel_vars:
            interpolator.add_path(v, [])
        return interpolator.interpolated_paths
    
    def convert_to_states(self) -> List[List[float]]:
        return [[element for key in sorted(self.trajectories.keys()) for element in self.trajectories[key][i]]
                for i in range(len(next(iter(self.trajectories.values()))))
        ]
        

class ColregPlot(TrajectoryReceiver, MyPlot):  
    def __init__(self,logical_scenario: LogicalScenario, 
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float, float]]]] = None): 
        MyPlot.__init__(self)
        TrajectoryReceiver.__init__(self, logical_scenario, trajectories)
        
        self.ship_markings_component = ShipMarkingsComponent(self.ax, self.logical_scenario)
        self.drawing_component = DrawingComponent(self.fig, self.ax, self.logical_scenario)
        self.legend_component = LegendComponent(self.ax, self.logical_scenario)
        self.vo_cone_component = VOConeComponent(self.ax, self.logical_scenario)
        self.add_vo_cone_component = AdditionalVOConeComponent(self.ax, self.logical_scenario)
        self.distance_component = DistanceComponent(self.ax, self.logical_scenario)
        self.angle_circle_component = AngleCircleComponent(self.ax, self.logical_scenario, linewidth=1.5)
        self.centered_angle_circle_component = CenteredAngleCircleComponent(self.ax, self.logical_scenario)          
        self.prime_component = PrimeComponent(self.ax, self.logical_scenario)
        self.ship_image_component = ShipImageComponent(self.ax, self.logical_scenario)    
        
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
         
        self.animation = ColregAnimation(self.fig, self.logical_scenario, self.components, self.convert_to_states())
        
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
        
        self.title = '\n'.join([rel.name for rel in self.logical_scenario.relations if rel.has_os()])
        for rel in self.logical_scenario.relations:
            rel.info() 
            
        aggregate = AggregateAll(env=self.logical_scenario, minimize=True)
        print(f'Penalty: {aggregate.loose_evaluate()}')                      
                        
        self.set_layout()    
        
        
    def set_layout(self):
        #self.fig.tight_layout(pad=10)
        self.ax.grid(False)
       
        #self.ax.set_title(f'USV situation\n{self.title}')
        self.ax.set_xlabel('X Position (m)')
        self.ax.set_ylabel('Y Position (m)')
        self.ax.set_aspect('equal', adjustable='box')      
        
        # Recalculate the limits based on the current data     
        self.ax.relim()
        
        self.fig.tight_layout()
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
           
        
        
        

    