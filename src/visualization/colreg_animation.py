import copy
from typing import Optional
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent

class ColregAnimation():
    
    ANIM_MAX_REAL_TIME = 60.0 * 30.0
    ANIM_MAX_SIM_TIME = 30.0
    
    FRAMES_PER_SEC = 10.0
    REAL_TIME = 1.0 / FRAMES_PER_SEC
    
    SPEED_UP_RATIO = ANIM_MAX_REAL_TIME / ANIM_MAX_SIM_TIME
    
    ANIM_MAX_FRAMES = ANIM_MAX_SIM_TIME * FRAMES_PER_SEC
    
    def __init__(self, fig : plt.Figure, ax: plt.Axes, env : USVEnvironment, components : list[PlotComponent],
                 trajectories : Optional[dict[int, list[tuple[float, float, float, float]]]] = None) -> None:
        self.ax = ax
        self.fig = fig
        self.env = env
        self.components = components
        self.is_anim_paused = True
        self.anim_frame_counter = 0
        self.anim = FuncAnimation(self.fig, self.update_graphs, self.update_anim, init_func=self.init_anim, blit=True, interval=int((1 / self.FRAMES_PER_SEC) * 1000), save_count=int(self.ANIM_MAX_FRAMES))
        self.trajectories = trajectories
        
    def update_anim(self):
        self.init_anim()
        while self.anim_frame_counter < self.ANIM_MAX_FRAMES:
            if not self.is_anim_paused:
                for o in self.din_env.vessels:
                    if self.trajectories is None:
                        vec = o.v * self.REAL_TIME * self.SPEED_UP_RATIO
                        o.update(o.p[0] + vec[0], o.p[1] + vec[1], o.heading, o.speed)
                    else:
                        traj = self.trajectories[str(o.id)]
                        frame = traj[int(self.anim_frame_counter * self.REAL_TIME * self.SPEED_UP_RATIO)]
                        o.update(frame[0], frame[1], frame[2], frame[3])
                for colreg_s in self.din_env.colreg_situations:
                    colreg_s.update()
                self.anim_frame_counter += 1
            yield self.din_env, self.anim_frame_counter
        
    def update_graphs(self, data):
        #self.auto_scale()
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
                print('Animation started')
            else:
                self.is_anim_paused = True
                print('Animation paused')
                
                
    def auto_scale(self):
        # Recalculate the limits based on the current data     
        self.ax.relim()
        # Automatically adjust xlim and ylim
        self.ax.autoscale_view(tight=True)
     
       