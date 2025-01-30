from datetime import datetime
import random
from typing import Dict, Optional
import matplotlib.pyplot as plt
import imageio

# Ignoring warnings for the educational purpose of this tutorial
import warnings

import numpy as np

from commonocean.planning.planning_problem import PlanningProblem
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.trajectory_manager import TrajectoryManager
from concrete_level.models.vessel_state import VesselState
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from logical_level.models.vessel_types import CargoShip, FishingShip, MilitaryVessel, MotorVessel, PassengerShip, VesselType
from utils.asv_utils import EGO_BEAM, EGO_LENGTH, vessel_radius
from utils.file_system_utils import ASSET_FOLDER, get_all_file_paths
from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager
warnings.filterwarnings('ignore')
from commonroad.geometry.shape import Rectangle
from commonocean.common.file_reader import CommonOceanFileReader
from commonocean.scenario.obstacle import ObstacleType

COMMON_OCEAN_PATH = f'{ASSET_FOLDER}/common_ocean_scenarios'
COMMON_OCEAN_TWO_VESSEL_SCENARIOS_PATH = f'{COMMON_OCEAN_PATH}/2vessel_scenarios'

obstacle_type_map : Dict[ObstacleType, VesselType]= {ObstacleType.CARGOSHIP : CargoShip(),
                     ObstacleType.FISHINGVESSEL : FishingShip(),
                     ObstacleType.MILITARYVESSEL : MilitaryVessel(),
                     ObstacleType.MOTORVESSEL : MotorVessel()}

def get_scene(file_path : str)-> Optional[ConcreteScene]:
    # read in the scenario and planning problem set
    scenario, planning_problem_set = CommonOceanFileReader(file_path).open()
    builder = SceneBuilder()
    vessel_id = 1
    for obst in scenario.dynamic_obstacles:
        if obst.obstacle_type in obstacle_type_map.keys():
            p = obst.initial_state.position
            speed = obst.initial_state.velocity
            heading = obst.initial_state.orientation
            vessel_type = obstacle_type_map[obst.obstacle_type]
            if isinstance(obst.obstacle_shape, Rectangle):  
                if obst.obstacle_shape.length > vessel_type.max_length or obst.obstacle_shape.length < vessel_type.min_length:
                    raise ValueError('Object length is out of vessel type limits. Adjust!')   
                if obst.obstacle_shape.width > vessel_type.max_beam or obst.obstacle_shape.width < vessel_type.min_beam:
                    raise ValueError('Object beam is out of vessel type limits. Adjust!')          
                builder.set_state(ConcreteVessel(vessel_id, False, obst.obstacle_shape.length, obst.obstacle_shape.length*4, vessel_type.max_speed, vessel_type.name, beam=obst.obstacle_shape.width),
                                VesselState(p[0], p[1], speed, heading))
                vessel_id += 1
    if len(builder) == 0:
        return None            
    planning_problem : PlanningProblem = list(planning_problem_set.planning_problem_dict.values())[0]
    id = planning_problem.planning_problem_id
    p = planning_problem.initial_state.position
    speed = planning_problem.initial_state.velocity
    heading = planning_problem.initial_state.orientation
    vessel_type = PassengerShip()
    builder.set_state(ConcreteVessel(0, True, EGO_LENGTH, vessel_radius(EGO_LENGTH), vessel_type.max_speed, vessel_type.name, beam = EGO_BEAM),
                                VesselState(p[0], p[1], speed, heading))       
    return builder.build()


# generate path of the file to be read
file_paths = get_all_file_paths(COMMON_OCEAN_TWO_VESSEL_SCENARIOS_PATH, 'xml')

for file_path in file_paths:
    scene = get_scene(file_path)
    if scene is None:
        continue
    eval_data = EvaluationData()
    eval_data.config_group = 'common_ocean_benchmark'
    eval_data.vessel_number = 2
    eval_data.measurement_name = f'test_{2}_vessel_scenarios'
    eval_data.algorithm_desc = 'ais_source'
    eval_data.scenario_name = f'{2}vessel'
    eval_data.timestamp = datetime.now().isoformat()   
    eval_data.best_scene = scene
    eval_data.best_fitness_index = 0.0
    eval_data.best_fitness = (0.0)
    eval_data.save_as_measurement()