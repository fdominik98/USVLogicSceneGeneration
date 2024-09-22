import copy
from typing import Dict, List, Tuple
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from model.usv_environment import USVEnvironment
from model.vessel import Vessel
from visualization.plot_component import PlotComponent

TWO_HOURS = 2 * 60 * 60
TWO_MINUTES = 2 * 60

ANIM_REAL_TIME = TWO_HOURS * 2
ANIM_SIM_TIME = TWO_MINUTES / 4

FRAMES_PER_SEC = 25.0
REAL_TIME = 1.0 / FRAMES_PER_SEC

class ColregAnimation():
    
    def speed_up_ratio(self):
        return self.real_time_value / self.sim_time_value
    
    def anim_max_frames(self):
        return self.sim_time_value * FRAMES_PER_SEC
    
    def get_sim_time_count(self) -> str:
        sim_time = self.anim_frame_counter / FRAMES_PER_SEC
        real_time = sim_time * self.speed_up_ratio()
        return f'Simulation time: {round(sim_time)} s, Real time: {round(real_time)} s'
    
    def __init__(self, fig : plt.Figure,
                 env : USVEnvironment, components : List[PlotComponent],
                 trajectories : Dict[int, List[Tuple[float, float, float, float]]]) -> None:
        self.fig = fig
        self.env = env
        self.components = components
        
        self.real_time_value = ANIM_REAL_TIME
        self.sim_time_value = ANIM_SIM_TIME

        self.trajectories = copy.deepcopy(trajectories)
        # for id in self.trajectories.keys():
        #     self.trajectories[id] = PathInterpolator.interpolate_headings(self.trajectories[id])
            
        self.anim = None
        self.init_anim()
            
    def start(self):
        self.anim = FuncAnimation(self.fig, self.update_graphs, self.update_anim, init_func=self.init_anim, blit=True, interval=int((1 / FRAMES_PER_SEC) * 1000), cache_frame_data=False)
        
    def update_anim(self):
        self.init_anim()
        while self.anim_frame_counter < self.anim_max_frames():
            if not self.is_anim_paused:
                for o in self.dyn_env.vessels:
                   o.update(*self.select_next_state(o))
                for colreg_s in self.dyn_env.colreg_situations:
                    colreg_s.update()
                self.anim_frame_counter += 1
            yield self.dyn_env
            
            
    def select_next_state(self, o: Vessel):
        speed_up = self.speed_up_ratio()
        traj = self.trajectories[o.id]
        frame_index = int(self.anim_frame_counter * REAL_TIME * speed_up)
        if frame_index < len(traj):                
            return traj[frame_index]
            
        vec = o.v * REAL_TIME * speed_up
        return (o.p[0] + vec[0], o.p[1] + vec[1], o.heading, o.speed)
        
    def update_graphs(self, data):
        #self.auto_scale()
        new_env = data
        return [graph for component in self.components for graph in component.update(new_env) if graph.get_visible()]
            
            
    def init_anim(self):
        self.dyn_env = copy.deepcopy(self.env)
        self.anim_frame_counter = 0
        self.is_anim_paused = True
        return [graph for component in self.components for graph in component.reset()]
    
    
    # Function to start or pause the animation
    def toggle_anim(self, event):
        if event.key == 'down':
            self.init_anim()
            print('Animation reset')
        elif event.key == 'up':
            if self.is_anim_paused:
                self.is_anim_paused = False
                if self.anim == None:
                    self.start()
                print('Animation started')
            else:
                self.is_anim_paused = True
                print('Animation paused')
                
                
    def auto_scale(self):
        for ax in self.fig.get_axes():
            # Recalculate the limits based on the current data    
            ax.relim()
            # Automatically adjust xlim and ylim
            ax.autoscale_view()
            
 
            
            