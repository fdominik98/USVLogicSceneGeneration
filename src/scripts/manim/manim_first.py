import copy
from typing import Any, Tuple
from manim import *
from manim.constants import DEFAULT_DOT_RADIUS, ORIGIN
from manim.utils.color import WHITE
from numpy import floating
from utils.file_system_utils import ASSET_FOLDER
from utils.asv_utils import MAX_COORD
from concrete_level.data_parser import EvalDataParser, TrajDataParser
from logical_level.models.logical_scenario import LoadedEnvironment
from functional_level.metamodels.functional_scenario import Vessel
from visualization.colreg_scenarios.scenario_plot import TrajectoryReceiver

light_colors = [BLUE_A, RED_A, GREEN_A, YELLOW_A, LIGHT_BROWN]
colors = [BLUE_C, RED_C, GREEN_C, YELLOW_C, DARK_BROWN]
       
        
class Animated(Mobject):
    def path_animate(self, mobject, t):
        pass
    
    def refresh_data(self):
        pass

class SimDot(Dot3D, Animated):
    def __init__(self, vessel : Vessel, axes : ThreeDAxes, traj: List[Tuple[float, float, float, float, float]],
                 def_traj: List[Tuple[float, float, float, float, float]]) -> None:
        self.traj = def_traj
        self.real_traj = traj
        self.def_traj = def_traj
        self.axes = axes
        self.vessel = vessel
        self.traj_length = len(self.traj) - 1
        self.refresh_data(z=200)
        super().__init__(self.point, color=colors[vessel.id], radius=DEFAULT_DOT_RADIUS / 4)
        self.refresh_data()
        self.generate_target()
        self.target.move_to(self.point) 
        
    def path_animate(self, mobject, t):
        index = int(self.traj_length * t)
        self.vessel.update(*self.traj[index])
        self.refresh_data()
        self.move_to(self.point)
        
    def refresh_data(self, z = 4):
        self.point = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], z)
        self.down_point = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], 0)
        
    def get_center_0z(self):
        return self.down_point
        
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
        
    def refresh_data(self, z = 4):
        self.point = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], z)
        self.v_end = (self.vessel.p + self.vessel.v*300)
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
        super().__init__(f'{ASSET_FOLDER}/images/ship_white.svg', height=0.03, width=0.03)
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
        super().__init__(radius=vessel.r / 750, color=colors[vessel.id], stroke_width=3)
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
        file1 = 'C:\\Users\\domfr93\\Desktop\\USVLogicSceneGeneration/assets/gen_data/RRTStar_algo/5vessel_MSR_10/test - 2024-11-18T08-37-24.458725/2024-11-18T08-38-24.408477.json'
        file2 = file1.replace('domfr93', 'freyd')
        traj = traj_parser.load_models_from_files([file1])
        env_path1 = traj[0].logical_scenario_path
        env_path2 = env_path1.replace('domfr93', 'freyd')
        data = data_parser.load_data_models_from_files([env_path1])
        self.logical_scenario = LoadedEnvironment(eval_data=data[0])
        self.trajectories = TrajectoryReceiver(self.logical_scenario, traj[0].trajectories)
        
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
        self.move_camera(frame_center=axes_3d.c2p(MAX_COORD*0.5, MAX_COORD*1, 10), zoom=2.5)
        self.wait(1)
        self.move_camera(phi=50 * DEGREES, theta=-45 * DEGREES, run_time=2)
        
        graphs : List[Animated] = []
        paths1 : List[TracedPath] = []
        paths2 : List[TracedPath] = []
                
        # Define two points with sufficient distance
        def_trajs = self.trajectories.gen_trajectories()
        for vessel in self.logical_scenario.vessel_vars:
            traj = self.trajectories.trajectories[vessel.id]
            def_traj = def_trajs[vessel.id]
            #rad = SimRadius(vessel, axes_3d, traj, def_traj)
            dot = SimDot(vessel, axes_3d, traj, def_traj)
            graphs += [dot,
                       SimVec(vessel, axes_3d, traj, def_traj),
                       SimImage(vessel, axes_3d, traj, def_traj)]
            
                    # Create a traced path for the moving object
            traced_path1 = TracedPath(
                dot.get_center_0z, 
                stroke_width=2.5, 
                stroke_color=light_colors[vessel.id],
                #dissipating_time=12
            )
            traced_path2 = TracedPath(
                dot.get_center_0z, 
                stroke_width=2.5, 
                stroke_color=light_colors[vessel.id],
                #dissipating_time=12
            )
            # Convert the traced path into a dashed path
            #dashed_path = DashedVMobject(traced_path, dashed_ratio=0.8)
            paths1 += [traced_path1]
            paths2 += [traced_path2]
            
        for g in graphs:
            self.add(g)
        
        self.wait(0.1)
        
        self.play(*[MoveToTarget(g) for g in graphs], rate_func=rate_functions.ease_in_quad, lag_ratio=0.2, run_time=1.2)
           
        self.wait(3)
        
        for p in paths1:
            self.add(p)
            
        self.play(*[UpdateFromAlphaFunc(g, g.path_animate) for g in graphs], rate_func=linear, lag_ratio=0, run_time=20)
        
        self.wait(2)
        for p in paths1:
            self.remove(p)
        for g in graphs:
            g.move_to(g.target)
        self.wait(2)
        for p in paths2:
            self.add(p)        
        
        for g in graphs:
            g.traj = g.real_traj
            g.traj_length = len(g.traj) - 1
            
        self.play(*[UpdateFromAlphaFunc(g, g.path_animate) for g in graphs], rate_func=linear, lag_ratio=0, run_time=35)
        
        self.wait(2)
        
        for p in paths2:
            p.traced_point_func = lambda: p.points[-1]
        
        for g in graphs:
            g.move_to(g.target)
            
        self.wait(5)