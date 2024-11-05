import copy
from manim import *
from model.environment.usv_config import ASSET_FOLDER, MAX_COORD
from model.data_parser import EvalDataParser, TrajDataParser
from model.environment.usv_environment import LoadedEnvironment
from src.model.vessel import Vessel
from src.visualization.colreg_scenarios.colreg_plot import TrajectoryReceiver

light_colors = [BLUE_A, RED_A, GREEN_A, YELLOW_A]
colors = [BLUE_C, RED_C, GREEN_C, YELLOW_C]
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
        
        # Create the first 2D axes on the yz-plane
        # axes_yz_1 = Axes(
        #     x_range=[0, MAX_COORD / 3, MAX_COORD / 15],  # y-axis values
        #     y_range=[0, MAX_COORD / 3, MAX_COORD / 15],  # z-axis values
        #     x_length=5,
        #     y_length=5,
        #     axis_config={"color": GREEN}
        # )
        # # Rotate and shift the first 2D axes to the yz-plane
        # axes_yz_1.rotate(PI / 2, axis=DOWN)
        # axes_yz_1.move_to(axes_3d.c2p(0,0,0))  # Adjust position as needed

        # # Create the second 2D axes on the yz-plane
        # axes_yz_2 = Axes(
        #     x_range=[0, MAX_COORD / 3, MAX_COORD / 15],  # y-axis values
        #     y_range=[0, MAX_COORD / 3, MAX_COORD / 15],  # z-axis values
        #     x_length=5,
        #     y_length=5,
        #     axis_config={"color": YELLOW}
        # )
        # # Rotate and shift the second 2D axes to the yz-plane
        # axes_yz_2.move_to(axes_3d.c2p(0,MAX_COORD/5,50))  # Adjust position as needed
        # axes_yz_2.rotate(PI / 2, axis=DOWN)

        # # Add the 3D and 2D axes to the scene
        # self.add(axes_yz_1, axes_yz_2)
        
        self.add(axes_3d, labels)
        self.move_camera(frame_center=axes_3d.center(), zoom=1)
        self.wait(1)
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=3)
        
        graphs : Dict[int, VesselData] = {}
        # Define two points with sufficient distance
        for vessel in self.env.vessels:
            data = VesselData(axes_3d, vessel)
            data.lift()
            graphs[vessel.id] = data
            self.add(data.ship_image, data.vec, data.dot, data.r,)
            
        self.wait(2)
        self.play(
            *[trans for v in self.env.vessels for trans in graphs[v.id].transform(VesselData(axes_3d, v))],
            run_time=1,
            rate_func=linear,
            lag_ratio=0
        )
            
        self.wait(0.5)        
        
        return
        self.dyn_env = copy.deepcopy(self.env)
        trajs = self.trajectories.convert_to_states()
        for i in range(0, len(trajs), 60):
            states = trajs[i]
            self.dyn_env.do_update(states)
            self.play(
                *[Create(Dot(graphs[v.id].point, color=light_colors[v.id], radius=DEFAULT_DOT_RADIUS/2)) for v in self.dyn_env.vessels],
                *[trans for v in self.dyn_env.vessels for trans in graphs[v.id].transform(VesselData(axes_3d, v))],
                run_time=0.3,
                rate_func=linear,
                lag_ratio=0
            )
