import copy
from typing import Dict, List, Optional, Tuple
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
from model.usv_environment import USVEnvironment
from model.vessel import Vessel
from visualization.plot_component import PlotComponent
from trajectory_planning.path_interpolator import PathInterpolator

class ColregAnimation():
    THREE_HOURS = 3 * 60 * 60
    TWO_MINUTES = 2 * 60
    
    ANIM_REAL_TIME = THREE_HOURS / 3
    ANIM_SIM_TIME = TWO_MINUTES / 2
    
    FRAMES_PER_SEC = 10.0
    REAL_TIME = 1.0 / FRAMES_PER_SEC
    
    SPEED_UP_RATIO = ANIM_REAL_TIME / ANIM_SIM_TIME
    
    ANIM_MAX_FRAMES = ANIM_SIM_TIME * FRAMES_PER_SEC
    
    def __init__(self, fig : plt.Figure,
                 env : USVEnvironment, components : List[PlotComponent],
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None) -> None:
        self.fig = fig
        self.env = env
        self.components = components
        self.is_anim_paused = True
        self.anim_frame_counter = 0
        self.rt_slider_ax = plt.axes((0.25, 0.15, 0.65, 0.03), facecolor='lightgoldenrodyellow')
        self.st_slider_ax = plt.axes((0.25, 0.05, 0.65, 0.03), facecolor='lightgoldenrodyellow')
        
        self.real_time_slider = Slider(self.rt_slider_ax, 'Real time', 10, self.THREE_HOURS, valinit=self.ANIM_REAL_TIME, valstep=10)
        self.sim_time_slider = Slider(self.st_slider_ax, 'Sim time', 1, self.TWO_MINUTES, valinit=self.ANIM_SIM_TIME, valstep=10)
      
        self.trajectories = None
        if trajectories is not None:
            self.trajectories = copy.deepcopy(trajectories)
            # for id in self.trajectories.keys():
            #     self.trajectories[id] = PathInterpolator.interpolate_headings(self.trajectories[id])
            
        self.anim = None
            
    def start(self):
        self.anim = FuncAnimation(self.fig, self.update_graphs, self.update_anim, init_func=self.init_anim, blit=True, interval=int((1 / self.FRAMES_PER_SEC) * 1000), save_count=int(self.ANIM_MAX_FRAMES))
        
    def update_anim(self):
        self.init_anim()
        while self.anim_frame_counter < self.ANIM_MAX_FRAMES:
            if not self.is_anim_paused:
                for o in self.din_env.vessels:
                   o.update(*self.select_next_state(o))
                for colreg_s in self.din_env.colreg_situations:
                    colreg_s.update()
                self.anim_frame_counter += 1
            yield self.din_env, self.anim_frame_counter
            
            
    def select_next_state(self, o: Vessel):
        if self.trajectories is not None:
            traj = self.trajectories[o.id]
            frame_index = int(self.anim_frame_counter * self.REAL_TIME * self.SPEED_UP_RATIO)
            if frame_index < len(traj):                
                return traj[frame_index]
            
        vec = o.v * self.REAL_TIME * self.SPEED_UP_RATIO
        return (o.p[0] + vec[0], o.p[1] + vec[1], o.heading, o.speed)
        
    def update_graphs(self, data):
        self.auto_scale()
        new_env, frame_id = data
        if frame_id % self.FRAMES_PER_SEC == 0 and not self.is_anim_paused:
            sim_time = frame_id / self.FRAMES_PER_SEC
            real_time = sim_time * self.SPEED_UP_RATIO
            print(f'Simulation time: {round(sim_time)} s, Real time: {round(real_time)}')
        return [graph for component in self.components for graph in component.update(new_env)]
            
            
    def init_anim(self):
        self.din_env = copy.deepcopy(self.env)
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
     
       