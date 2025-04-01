from datetime import datetime
from typing import Dict, List
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_actors import ConcreteVessel
from concrete_level.models.actor_state import ActorState
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from utils.vessel_types import ALL_VESSEL_TYPES, CargoShip, FishingShip, MilitaryVessel, MotorVessel, VesselType
from global_config import GlobalConfig, vessel_radius
from utils.file_system_utils import COMMON_OCEAN_FOLDER, get_all_file_paths
from commonroad.geometry.shape import Rectangle
from commonocean.common.file_reader import CommonOceanFileReader
from commonocean.scenario.obstacle import ObstacleType

COMMON_OCEAN_TWO_VESSEL_SCENARIOS_PATH = f'{COMMON_OCEAN_FOLDER}/HandcraftedTwoVesselEncounters_01_24'
COMMON_OCEAN_FLO_SCENARIOS_PATH = f'{COMMON_OCEAN_FOLDER}/Florida'
COMMON_OCEAN_MEC_SCENARIOS_PATH = f'{COMMON_OCEAN_FOLDER}/MiddleEastCoast'
COMMON_OCEAN_UWC_SCENARIOS_PATH = f'{COMMON_OCEAN_FOLDER}/UpperWestCoast'

obstacle_type_map : Dict[ObstacleType, VesselType]= {ObstacleType.CARGOSHIP : CargoShip(),
                     ObstacleType.FISHINGVESSEL : FishingShip(),
                     ObstacleType.MILITARYVESSEL : MilitaryVessel(),
                     ObstacleType.MOTORVESSEL : MotorVessel()}

def get_scenes(file_path : str)-> List[ConcreteScene]:
    scenes : List[ConcreteScene] = []
    # read in the scenario and planning problem set
    scenario, planning_problem_set = CommonOceanFileReader(file_path).open()
    builder = SceneBuilder()
    vessel_id = 1
    for obst in scenario.dynamic_obstacles:
        if obst.obstacle_type is None or obst.obstacle_type in obstacle_type_map.keys():
            p = obst.initial_state.position
            speed = obst.initial_state.velocity
            heading = obst.initial_state.orientation
            vessel_type = obstacle_type_map[obst.obstacle_type]
            if isinstance(obst.obstacle_shape, Rectangle):  
                if not vessel_type.do_match( obst.obstacle_shape.length, speed, obst.obstacle_shape.width):
                    raise ValueError('Object attributes is out of vessel type limits. Adjust!')   
                
                builder.set_state(ConcreteVessel(id=vessel_id,
                                                 is_os=False,
                                                 length=obst.obstacle_shape.length,
                                                 radius=vessel_radius(obst.obstacle_shape.length),
                                                 max_speed=vessel_type.max_speed,
                                                 type=vessel_type.name,
                                                 beam=obst.obstacle_shape.width),
                                ActorState(p[0], p[1], speed, heading))
                vessel_id += 1
    if len(builder) == 0:
        return scenes   
     
    ego_vessel_type = ALL_VESSEL_TYPES[GlobalConfig.OS_VESSEL_TYPE]
    ego_vessel = ConcreteVessel(id=0,
                                is_os=True,
                                length=ego_vessel_type.max_length,
                                radius=vessel_radius(ego_vessel_type.max_length),
                                max_speed=ego_vessel_type.max_speed,
                                type=GlobalConfig.OS_VESSEL_TYPE,
                                beam = ego_vessel_type.max_beam)
    for planning_problem in planning_problem_set.planning_problem_dict.values():
        p = planning_problem.initial_state.position
        speed = planning_problem.initial_state.velocity
        heading = planning_problem.initial_state.orientation
        builder.set_state(ego_vessel, ActorState(p[0], p[1], speed, heading))       
        scenes.append(builder.build())
    return scenes


# generate path of the file to be read
file_paths = (get_all_file_paths(COMMON_OCEAN_TWO_VESSEL_SCENARIOS_PATH, 'xml') + get_all_file_paths(COMMON_OCEAN_FLO_SCENARIOS_PATH, 'xml') +
                get_all_file_paths(COMMON_OCEAN_MEC_SCENARIOS_PATH, 'xml') + get_all_file_paths(COMMON_OCEAN_UWC_SCENARIOS_PATH, 'xml'))

for file_path in file_paths:
    scenes = get_scenes(file_path)
    for scene in scenes:
        eval_data = EvaluationData()
        eval_data.config_group = 'common_ocean_benchmark'
        eval_data.vessel_number = scene.actor_number
        eval_data.measurement_name = f'test_{scene.actor_number}_vessel_scenarios_long'
        eval_data.algorithm_desc = 'ais_source'
        eval_data.scenario_name = f'{scene.actor_number}vessel'
        eval_data.timestamp = datetime.now().isoformat()   
        eval_data.best_scene = scene
        eval_data.best_fitness_index = 0.0
        eval_data.best_fitness = (0.0)
        eval_data.save_as_measurement()