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
class VesselData():
    def __init__(self, axes : ThreeDAxes, vessel: Vessel) -> None:
        self.point = axes.c2p(vessel.p[0], vessel.p[1], 0)
        self.point_lifted = axes.c2p(vessel.p[0], vessel.p[1], 10)
        v_end = (vessel.p + vessel.v*500)
        end_lifted = axes.c2p(v_end[0], v_end[1], 10)
        
        self.dot = Dot(self.point_lifted, color=colors[vessel.id])
        self.vec = Arrow(self.point_lifted, end_lifted, color=colors[vessel.id])
        self.r = Circle(radius=vessel.r / 300, color=light_colors[vessel.id], stroke_width=3).move_to(self.point)
        self.ship_image = SVGMobject(f'{ASSET_FOLDER}/images/ship_white.svg', height=0.3, width=0.3)
        self.ship_image.move_to(self.point)
        self.ship_image.rotate(vessel.heading - PI / 2)
        
    def transform(self, new):
        transforms = [ReplacementTransform(self.dot, new.dot),
                ReplacementTransform(self.vec, new.vec),
                ReplacementTransform(self.r, new.r),
                ReplacementTransform(self.ship_image, new.ship_image),]
        
        self.dot = new.dot
        self.vec = new.vec
        self.r = new.r
        self.ship_image = new.ship_image
        self.point = new.point
        return transforms
    
    def lift(self):
        self.dot.set_z(5000)
        self.vec.set_z(5000)
        self.r.set_z(5000)
        self.ship_image.set_z(5000)
        
        
        
class Animated(Mobject):
    def animate(self, mobject, t):
        pass
    
    def refresh_data(self):
        pass

class SimDot(Dot, Animated):
    def __init__(self, vessel : Vessel, axes : ThreeDAxes, traj: List[Tuple[float, float, float, float, float]]) -> None:
        self.traj = traj
        self.axes = axes
        self.vessel = vessel
        self.traj_length = len(self.traj) - 1
        self.refresh_data()
        super().__init__(self.point_lifted, color=colors[vessel.id])
        
    def animate(self, mobject, t):
        index = int(self.traj_length * t)
        self.vessel.update(*self.traj[index])
        self.refresh_data()
        self.move_to(self.point_lifted)
        
    def refresh_data(self):
        self.point_lifted = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], 10)
        
class SimVec(Arrow, Animated):
    def __init__(self, vessel : Vessel, axes : ThreeDAxes, traj: List[Tuple[float, float, float, float, float]]) -> None:
        self.traj = traj
        self.axes = axes
        self.vessel = vessel
        self.traj_length = len(self.traj) - 1
        self.refresh_data()
        super().__init__(self.point_lifted, self.end_lifted, color=colors[vessel.id])
        
    def animate(self, mobject, t):
        index = int(self.traj_length * t)
        self.vessel.update(*self.traj[index])
        self.refresh_data()
        self._set_start_and_end_attrs(self.point_lifted, self.end_lifted)
        
    def refresh_data(self):
        self.point_lifted = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], 10)
        self.v_end = (self.vessel.p + self.vessel.v*500)
        self.end_lifted = self.axes.c2p(self.v_end[0], self.v_end[1], 10)
        
        
class SimImage(SVGMobject, Animated):
     def __init__(self, vessel : Vessel, axes : ThreeDAxes, traj: List[Tuple[float, float, float, float, float]]) -> None:
        self.traj = traj
        self.axes = axes
        self.vessel = vessel
        self.traj_length = len(self.traj) - 1
        self.refresh_data()
        super().__init__(f'{ASSET_FOLDER}/images/ship_white.svg', height=0.3, width=0.3)
        
     def refresh_data(self):
        self.point = self.axes.c2p(self.vessel.p[0], self.vessel.p[1], 0)
        
     def animate(self, mobject, t):
        index = int(self.traj_length * t)
        self.vessel.update(*self.traj[index])
        self.refresh_data()
        self.move_to(self.point)
        self.set_sheen_direction(self.vessel.heading)
        
        
class PointsWithVectorsAndRadius(ThreeDScene):
    def construct(self):
        
        data_parser = EvalDataParser()
        traj_parser = TrajDataParser()
        traj = traj_parser.load_models_from_files(['C:\\Users\\domfr93\\Desktop\\USVLogicSceneGeneration/assets/gen_data/RRTStar_algo/3vessel_MSR_1/test - 2024-11-04T14-06-27.604479/2024-11-04T14-07-17.930114.json'])
        data = data_parser.load_data_models_from_files([traj[0].env_path])
        self.env = LoadedEnvironment(eval_data=data[0])
        self.trajectories = TrajectoryReceiver(self.env, traj[0].trajectories)
        
        # Set the background color to white
        axes_3d = ThreeDAxes(x_range=[0, MAX_COORD*3, MAX_COORD*3 / 5],
                             y_range=[0, MAX_COORD*3, MAX_COORD*3 / 5],
                             z_range=[0,200, 200],
                             axis_config={"decimal_number_config": {"num_decimal_places": 0}},
                             x_axis_config={"numbers_to_include": [int(val) for val in np.arange(0, MAX_COORD*3, MAX_COORD *3 / 5)]},
                             y_axis_config={"numbers_to_include": [int(val) for val in np.arange(0, MAX_COORD*3, MAX_COORD *3 / 5)]},
                             tips=False,)
        labels = axes_3d.get_axis_labels(x_label=Tex("x (m)"), y_label=Tex("y (m)"))
                
        self.add(axes_3d, labels)
        self.move_camera(frame_center=axes_3d.center(), zoom=1)
        self.wait(1)
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=3)
        
        graphs : List[Animated] = []
        # Define two points with sufficient distance
        for vessel in self.env.vessels:
            traj = self.trajectories.trajectories[vessel.id]
            graphs += [SimDot(vessel, axes_3d, traj), SimVec(vessel, axes_3d, traj), SimImage(vessel, axes_3d, traj)]
            
        for g in graphs:
            self.add(g)
            
        self.wait(2)

        self.play(*[UpdateFromAlphaFunc(g, g.animate) for g in graphs], rate_func=linear, lag_ratio=0, run_time=10)