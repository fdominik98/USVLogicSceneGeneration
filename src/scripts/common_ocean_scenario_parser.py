import matplotlib.pyplot as plt
import imageio

# Ignoring warnings for the educational purpose of this tutorial
import warnings

from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from utils.file_system_utils import ASSET_FOLDER
warnings.filterwarnings('ignore')
from concrete_level.common_ocean.common.file_reader import CommonOceanFileReader
from concrete_level.common_ocean.visualization.draw_dispatch_cr import draw_object
from commonroad.visualization.mp_renderer import MPRenderer

COMMON_OCEAN_PATH = f'{ASSET_FOLDER}/common_ocean_scenarios'

# generate path of the file to be read
file_path = f"{COMMON_OCEAN_PATH}/ZAM_AAA-1_20240121_T-0.xml"

# read in the scenario and planning problem set
scenario, planning_problem_set = CommonOceanFileReader(file_path).open()

builder = SceneBuilder()
for obst in scenario.dynamic_obstacles:
    if obst.obstacle_type
        speed = np.linalg.norm(obj.velocity)
        valid_types = [t for t in ALL_VESSEL_TYPES if t.do_match(obj.length, speed)]
        vessel_type = PassengerShip() if obj.is_os else random.choice(valid_types)
        builder.set_state(ConcreteVessel(obj.id, obj.is_os, obj.length, obj.length*4, obj.max_speed, vessel_type.name),
                        VesselState(obj.position[0], obj.position[1], speed, calculate_heading(obj.velocity[0], obj.velocity[1])))
eval_data.best_scene = builder.build()