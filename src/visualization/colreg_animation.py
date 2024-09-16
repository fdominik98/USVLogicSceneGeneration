import copy
from typing import Dict, List, Tuple
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
from model.usv_environment import USVEnvironment
from model.vessel import Vessel
from visualization.plot_component import PlotComponent

class ColregAnimation():
    TWO_HOURS = 2 * 60 * 60
    TWO_MINUTES = 2 * 60
    
    ANIM_REAL_TIME = TWO_HOURS * 2
    ANIM_SIM_TIME = TWO_MINUTES / 4
    
    FRAMES_PER_SEC = 25.0
    REAL_TIME = 1.0 / FRAMES_PER_SEC
    
    def speed_up_ratio(self):
        return self.real_time_slider.val / self.sim_time_slider.val
    
    def anim_max_frames(self):
        return self.sim_time_slider.val * self.FRAMES_PER_SEC
    
    def get_sim_time_count(self, frame_id) -> str:
        sim_time = frame_id / self.FRAMES_PER_SEC
        real_time = sim_time * self.speed_up_ratio()
        return f'Simulation time: {round(sim_time)} s, Real time: {round(real_time)} s'
    
    def __init__(self, fig : plt.Figure,
                 env : USVEnvironment, components : List[PlotComponent],
                 trajectories : Dict[int, List[Tuple[float, float, float, float]]]) -> None:
        self.fig = fig
        self.env = env
        self.components = components
        self.is_anim_paused = True
        
        self.time_counter_ax : plt.Axes = plt.axes((0.25, 0.08, 0.65, 0.03))
        self.time_counter_ax.axis(False)
        self.rt_slider_ax : plt.Axes = plt.axes((0.25, 0.05, 0.65, 0.015))
        self.st_slider_ax : plt.Axes = plt.axes((0.25, 0.03, 0.65, 0.015))
        
        self.real_time_slider = Slider(self.rt_slider_ax, 'Real time', 10, self.TWO_HOURS * 4, valinit=self.ANIM_REAL_TIME, valstep=10)
        self.sim_time_slider = Slider(self.st_slider_ax, 'Sim time', 10, self.TWO_MINUTES, valinit=self.ANIM_SIM_TIME, valstep=10)
        self.time_counter_text = self.time_counter_ax.text(0, 0, self.get_sim_time_count(0), fontsize=12, color='black')

        self.trajectories = copy.deepcopy(trajectories)
        # for id in self.trajectories.keys():
        #     self.trajectories[id] = PathInterpolator.interpolate_headings(self.trajectories[id])
            
        self.anim = None
            
    def start(self):
        self.anim = FuncAnimation(self.fig, self.update_graphs, self.update_anim, init_func=self.init_anim, blit=True, interval=int((1 / self.FRAMES_PER_SEC) * 1000), cache_frame_data=False)
        
    def update_anim(self):
        self.init_anim()
        while self.anim_frame_counter < self.anim_max_frames():
            if not self.is_anim_paused:
                for o in self.dyn_env.vessels:
                   o.update(*self.select_next_state(o))
                for colreg_s in self.dyn_env.colreg_situations:
                    colreg_s.update()
                self.anim_frame_counter += 1
            yield self.dyn_env, self.anim_frame_counter
            
            
    def select_next_state(self, o: Vessel):
        speed_up = self.speed_up_ratio()
        traj = self.trajectories[o.id]
        frame_index = int(self.anim_frame_counter * self.REAL_TIME * speed_up)
        if frame_index < len(traj):                
            return traj[frame_index]
            
        vec = o.v * self.REAL_TIME * speed_up
        return (o.p[0] + vec[0], o.p[1] + vec[1], o.heading, o.speed)
        
    def update_graphs(self, data):
        #self.auto_scale()
        new_env, frame_id = data
        if frame_id % self.FRAMES_PER_SEC == 0 and not self.is_anim_paused:
            self.time_counter_text.set_text(self.get_sim_time_count(frame_id))
        return [graph for component in self.components for graph in component.update(new_env)] + [self.time_counter_text]
            
            
    def init_anim(self):
        self.dyn_env = copy.deepcopy(self.env)
        self.anim_frame_counter = 0
        self.is_anim_paused = True
        self.time_counter_text.set_text(self.get_sim_time_count(0))
        return [graph for component in self.components for graph in component.reset()] + [self.time_counter_text]
    
    
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
            
            