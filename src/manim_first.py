import copy
from typing import Any, Tuple
from manim import *
from manim.constants import DEFAULT_DOT_RADIUS, ORIGIN
from manim.utils.color import WHITE
from numpy import floating
from model.environment.usv_config import ASSET_FOLDER, MAX_COORD
from model.data_parser import EvalDataParser, TrajDataParser
from model.environment.usv_environment import LoadedEnvironment
from src.model.vessel import Vessel
from src.visualization.colreg_scenarios.colreg_plot import TrajectoryReceiver

light_colors = [BLUE_A, RED_A, GREEN_A, YELLOW_A, LIGHT_BROWN]
colors = [BLUE_C, RED_C, GREEN_C, YELLOW_C, DARK_BROWN]
       
        
class Animated(Mobject):
    def path_animate(self, mobject, t):
        pass
    
    def refresh_data(self):
        pass

class SimDot(Dot, Animated):
    def __init__(self, vessel : Vessel, axes : ThreeDAxes, traj: List[Tuple[float, float, float, float, float]],
                 def_traj: List[Tuple[float, float, float, float, float]]) -> None:
        self.traj = def_traj
        self.real_traj = traj
        self.def_traj = def_traj
        self.axes = axes
        self.vessel = vessel
        self.traj_length = len(self.traj) - 1
        self.refresh_data(z=200)
        super().__init__(self.point, color=colors[vessel.id])
        self.refresh_data()
        self.generate_target()
        self.target.move_to(self.point) 
        
    def path_animate(self, mobject, t):
        index = int(self.traj_length * t)
        self.vessel.update(*self.traj[index])
        self.refresh_data()
        self.move_to(self.point)
        
    def refresh_data(self, z = 10):
        self.point = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], z)
        
class SimVec(Arrow, Animated):
    def __init__(self, vessel : Vessel, axes : ThreeDAxes, traj: List[Tuple[float, float, float, float, float]],
                 def_traj: List[Tuple[float, float, float, float, float]]) -> None:
        self.traj = def_traj
        self.real_traj = traj
        self.def_traj = def_traj
        self.axes = axes
        self.vessel = vessel
        self.traj_length = len(self.traj) - 1
        self.refresh_data(z=200)
        super().__init__(self.point, self.end, color=colors[vessel.id])
        self.refresh_data()
        self.generate_target()
        self.target.put_start_and_end_on(self.point, self.end)
        
    def path_animate(self, mobject, t):
        index = int(self.traj_length * t)
        self.vessel.update(*self.traj[index])
        self.refresh_data()
        self.put_start_and_end_on(self.point, self.end)
        
    def refresh_data(self, z = 10):
        self.point = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], z)
        self.v_end = (self.vessel.p + self.vessel.v*600)
        self.end = self.axes.c2p(self.v_end[0], self.v_end[1], z)
        
        
class SimImage(SVGMobject, Animated):
     def __init__(self, vessel : Vessel, axes : ThreeDAxes, traj: List[Tuple[float, float, float, float, float]],
                 def_traj: List[Tuple[float, float, float, float, float]]) -> None:
        self.traj = def_traj
        self.real_traj = traj
        self.def_traj = def_traj
        self.axes = axes
        self.vessel = vessel
        self.traj_length = len(self.traj) - 1
        self.refresh_data(z=200)
        super().__init__(f'{ASSET_FOLDER}/images/ship_white.svg', height=0.1, width=0.1)
        self.move_to(self.point)
        self.rotate(self.vessel.heading - PI / 2)
        self.angle = self.vessel.heading - PI / 2
        self.refresh_data()
        self.generate_target()
        self.target.move_to(self.point) 
        
     def refresh_data(self, z = 0):
        self.point = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], z)
        
     def path_animate(self, mobject, t):
        index = int(self.traj_length * t)
        self.vessel.update(*self.traj[index])
        self.refresh_data()
        self.move_to(self.point)
        self.rotate((self.vessel.heading - PI/2) - self.angle)
        self.angle = self.vessel.heading - PI / 2
        
class SimRadius(Circle, Animated):
    def __init__(self, vessel : Vessel, axes : ThreeDAxes, traj: List[Tuple[float, float, float, float, float]],
                 def_traj: List[Tuple[float, float, float, float, float]]) -> None:
        self.traj = def_traj
        self.real_traj = traj
        self.def_traj = def_traj
        self.axes = axes
        self.vessel = vessel
        self.traj_length = len(self.traj) - 1
        self.refresh_data(z=200)
        super().__init__(radius=vessel.r / 600, color=light_colors[vessel.id], stroke_width=3)
        self.move_to(self.point)
        self.refresh_data()
        self.generate_target()
        self.target.move_to(self.point) 
        
    def path_animate(self, mobject, t):
        index = int(self.traj_length * t)
        self.vessel.update(*self.traj[index])
        self.refresh_data()
        self.move_to(self.point)     

        
    def refresh_data(self, z = 0):
        self.point = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], z)
        
        
class PointsWithVectorsAndRadius(ThreeDScene):
    def construct(self):
        
        data_parser = EvalDataParser()
        traj_parser = TrajDataParser()
        file1 = 'C:\\Users\\domfr93\\Desktop\\USVLogicSceneGeneration/assets/gen_data/RRTStar_algo/3vessel_MSR_1/test - 2024-11-04T14-06-27.604479/2024-11-04T14-07-17.930114.json'
        file2 = file1.replace('domfr93', 'freyd')
        traj = traj_parser.load_models_from_files([file2])
        env_path1 = traj[0].env_path
        env_path2 = env_path1.replace('domfr93', 'freyd')
        data = data_parser.load_data_models_from_files([env_path2])
        self.env = LoadedEnvironment(eval_data=data[0])
        self.trajectories = TrajectoryReceiver(self.env, traj[0].trajectories)
        
        # Set the background color to white
        axes_3d = ThreeDAxes(x_range=[-MAX_COORD, MAX_COORD*3, MAX_COORD*3 / 5],
                             y_range=[-MAX_COORD, MAX_COORD*3, MAX_COORD*3 / 5],
                             z_range=[0, 200, 200],
                             axis_config={"decimal_number_config": {"num_decimal_places": 0}},
                             x_axis_config={"numbers_to_include": [int(val) for val in np.arange(-MAX_COORD, MAX_COORD*3, MAX_COORD *3 / 5)]},
                             y_axis_config={"numbers_to_include": [int(val) for val in np.arange(-MAX_COORD, MAX_COORD*3, MAX_COORD *3 / 5)]},
                             tips=True,)
        labels = axes_3d.get_axis_labels(x_label=Tex("x (m)"), y_label=Tex("y (m)"))
                
        self.add(axes_3d, labels)
        self.move_camera(frame_center=axes_3d.c2p(2*MAX_COORD, MAX_COORD , 20), zoom=1)
        self.wait(1)
        self.move_camera(phi=50 * DEGREES, theta=-45 * DEGREES, run_time=3)
        
        graphs : List[Animated] = []
        # Define two points with sufficient distance
        def_trajs = self.trajectories.gen_trajectories()
        for vessel in self.env.vessels:
            traj = self.trajectories.trajectories[vessel.id]
            def_traj = def_trajs[vessel.id]
            graphs += [SimDot(vessel, axes_3d, traj, def_traj),
                       SimVec(vessel, axes_3d, traj, def_traj),
                       SimImage(vessel, axes_3d, traj, def_traj), 
                       SimRadius(vessel, axes_3d, traj, def_traj)]
            
        for g in graphs:
            self.add(g)
        
        self.wait(0.1)
        
        self.play(*[MoveToTarget(g) for g in graphs], rate_func=rate_functions.ease_in_quad, lag_ratio=0.15, run_time=0.7)
           
        self.wait(2)
        
        self.play(*[UpdateFromAlphaFunc(g, g.path_animate) for g in graphs], rate_func=linear, lag_ratio=0, run_time=15)
        
        self.wait(1)
        
        for g in graphs:
            g.traj = g.real_traj
            g.traj_length = len(g.traj) - 1
            
        self.play(*[UpdateFromAlphaFunc(g, g.path_animate) for g in graphs], rate_func=linear, lag_ratio=0, run_time=15)