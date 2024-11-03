from manim import *
from model.environment.usv_config import ASSET_FOLDER, MAX_COORD
from model.data_parser import EvalDataParser
from model.environment.usv_environment import LoadedEnvironment



class PointsWithVectorsAndRadius(ThreeDScene):
    def construct(self):
        
        colors = [BLUE, RED, GREEN, YELLOW]
        light_colors = [BLUE_C, RED_C, GREEN_C, YELLOW_C]
        data_parser = EvalDataParser()
        data = data_parser.load_data_models_from_files(['C:\\Users\\freyd\\Desktop\\USVLogicSceneGeneration\\assets\\gen_data\\test_3_vessel_scenarios_MSR\\MSR\\pymoo_NSGA2_algorithm_vessel\\3vessel_MSR_1_2024-10-21T10-33-12.924391.json'])
        env = LoadedEnvironment(eval_data=data[0])
        
        # Set the background color to white
        axes_3d = ThreeDAxes(x_range=[0, MAX_COORD, MAX_COORD / 5],
                             y_range=[0, MAX_COORD, MAX_COORD / 5],
                             z_range=[0,200, 200])
        
        self.add(axes_3d)
        
        self.move_camera(frame_center=axes_3d.c2p(MAX_COORD/2, MAX_COORD/2, 100), zoom=0.8)
        
                # Create the first 2D axes on the yz-plane
        axes_yz_1 = Axes(
            x_range=[0, MAX_COORD / 3, MAX_COORD / 15],  # y-axis values
            y_range=[0, MAX_COORD / 3, MAX_COORD / 15],  # z-axis values
            x_length=5,
            y_length=5,
            axis_config={"color": GREEN}
        )
        # Rotate and shift the first 2D axes to the yz-plane
        axes_yz_1.rotate(PI / 2, axis=DOWN)
        axes_yz_1.move_to(axes_3d.c2p(0,0,0))  # Adjust position as needed

        # Create the second 2D axes on the yz-plane
        axes_yz_2 = Axes(
            x_range=[0, MAX_COORD / 3, MAX_COORD / 15],  # y-axis values
            y_range=[0, MAX_COORD / 3, MAX_COORD / 15],  # z-axis values
            x_length=5,
            y_length=5,
            axis_config={"color": YELLOW}
        )
        # Rotate and shift the second 2D axes to the yz-plane
        axes_yz_2.move_to(axes_3d.c2p(0,MAX_COORD/5,50))  # Adjust position as needed
        axes_yz_2.rotate(PI / 2, axis=DOWN)

        # Add the 3D and 2D axes to the scene
        self.add(axes_yz_1, axes_yz_2)
        
        
        # Define two points with sufficient distance
        for vessel in env.vessels:
            point = axes_3d.c2p(vessel.p[0], vessel.p[1], 0)
            point_lifted = axes_3d.c2p(vessel.p[0], vessel.p[1], 10)
            v_end = (vessel.p + vessel.v*500)
            end_lifted = axes_3d.c2p(v_end[0], v_end[1], 10)
            dot = Dot3D(point_lifted, color=colors[vessel.id])
            vec = Arrow3D(point_lifted, end_lifted, color=colors[vessel.id])
            r = Circle(radius=vessel.r / 300, color=light_colors[vessel.id]).move_to(point)
            ship_image = SVGMobject(f'{ASSET_FOLDER}/images/ship_white.svg', height=0.3, width=0.3)
            ship_image.move_to(point)
            ship_image.rotate(vessel.heading - PI / 2)
            self.add(ship_image, vec, dot, r,)
        self.wait(2)

        # Transition to 3D view with a camera rotation and add 3D axes for perspective
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=3)
        
        # Wait to display the final 3D perspective
        self.wait(2)