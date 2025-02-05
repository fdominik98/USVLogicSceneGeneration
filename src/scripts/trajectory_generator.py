from datetime import datetime
from itertools import chain
import os
import random
from typing import List, Dict
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from concrete_level.models.trajectories import Trajectories
from concrete_level.models.trajectory_manager import TrajectoryManager
from concrete_level.trajectory_generation.trajectory_builder import TrajectoryBuilder
from utils.file_system_utils import ASSET_FOLDER
from utils.asv_utils import MAX_COORD
from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager
from concrete_level.models.rrt_models import Obstacle, PolygonalObstacle, LineObstacle, CircularObstacle
from concrete_level.models.vessel_order_graph import VesselNode, VesselOrderGraph
from concrete_level.trajectory_generation.trajectory_data import TrajectoryData
from concrete_level.trajectory_generation.path_interpolator import PathInterpolator
from concrete_level.data_parser import EvalDataParser
import numpy as np
from concrete_level.trajectory_generation.bidirectional_rrt_star_fnd import BidirectionalRRTStarFND, DIM

SCALER = 1 / MAX_COORD / 1.5  * DIM

DIRECTION_THRESHOLD = 100 # meter
GOAL_SAMPLE_RATE = 5.0 #%

measurement_name = 'test'
measurement_id = f"{measurement_name} - {datetime.now().isoformat().replace(':','-')}"

seed = 1234
random.seed(seed)
np.random.seed(seed)

def find_center_and_radius(points_array):
    # Calculate the center (centroid) by averaging the coordinates
    center = np.mean(points_array, axis=0)
    # Calculate the radius as the maximum distance from the center to any point
    distances = np.linalg.norm(points_array - center, axis=1)
    radius = np.max(distances)
    return center, radius


dp = EvalDataParser()
data_models = dp.load_data_models()

if len(data_models) == 0:
    exit(0)

eval_data = data_models[0]
trajectory_manager = TrajectoryManager(eval_data.best_scene)
ScenarioPlotManager(trajectory_manager)
scenario = trajectory_manager.scenario

def run_trajectory_generation(vessel : ConcreteVessel, interpolator : PathInterpolator):
    vessel_state = scenario.concrete_scene[vessel]
    print(f'Calculation {vessel}:')
    expand_distance = vessel_state.speed * 20 # half minute precision
    
    if len(v_node.relations) == 0:
        return [], 0, expand_distance
    
    obstacle_list : List[Obstacle] = []
    collision_points : List[np.ndarray] = []
    
    for obj1, obj2 in v_node.relations:
        print(f'Collision points for static colreg ({obj1}, {obj2})')
        var1 = scenario.to_variable(obj1)
        var2 = scenario.to_variable(obj2)
        colreg_collision_points = scenario.evaluation_cache.get_collision_points(var1, var2)
        collision_points += [p for p in colreg_collision_points]
    
    new_trajectory_builder = TrajectoryBuilder(interpolator.trajectory_builder)    
    new_trajectory_builder.add_state(vessel, vessel_state)
    new_trajectory_builder.even_lengths()
    collision_points += chain.from_iterable(new_trajectory_builder.build().collision_points)
        
    furthest_collision_point = max(collision_points, key=lambda p: np.linalg.norm(p - vessel_state.p))
    
    if len(collision_points) != 0:
        collision_center, _ = find_center_and_radius(collision_points)
    else:
        collision_center = vessel_state.p + vessel_state.v * interpolator.path_length / 2
    
    start_coll_center_dist = np.linalg.norm(vessel_state.p - collision_center)
    start_furthest_point_dist = np.linalg.norm(vessel_state.p - furthest_collision_point)
    start_goal_dist = start_coll_center_dist * 2
    goal_vector = vessel_state.v_norm * start_goal_dist
    goal = vessel_state.p + goal_vector
    max_sized_vessel = max(interpolator.trajectory_builder.keys(), key=lambda v: v.radius)
    min_go_around_dist = (max_sized_vessel.radius + vessel.radius) * 2
    
    poly_p1 = vessel_state.p + vessel_state.v_norm * start_coll_center_dist / 3
    poly_p2 = vessel_state.p + vessel_state.v_norm * start_furthest_point_dist
    poly_p3 = poly_p2 + vessel_state.v_norm_perp * min_go_around_dist
    poly_p4 = poly_p1 + vessel_state.v_norm_perp * min_go_around_dist
        
    obstacle_list += [PolygonalObstacle(p1=poly_p1, p2=poly_p2, p3=poly_p3, p4=poly_p4)]    
    obstacle_list += [CircularObstacle(p, v.r) for p in collision_points]
    
    # Define the bounding lines
    min_go_around_line = LineObstacle(vessel.p[0], vessel.p[1], vessel.v_norm(), False, min_go_around_dist)
    go_around_split_line = LineObstacle(collision_center[0], collision_center[1], vessel.v_norm_perp(), False, 0)
    
    bounding_lines = [
        LineObstacle(vessel.p[0], vessel.p[1], vessel.v_norm(), True, DIRECTION_THRESHOLD),   # Left bounding line
        LineObstacle(goal[0], goal[1], vessel.v_norm(), False, min_go_around_dist * 5), # Right bounding line
        LineObstacle(vessel.p[0], vessel.p[1], vessel.v_norm(), False, min_go_around_dist * 5), # Right bounding line
        LineObstacle(vessel.p[0], vessel.p[1], vessel.v_norm_perp(), False, DIRECTION_THRESHOLD), # Behind bounding line
        LineObstacle(goal[0], goal[1], vessel.v_norm_perp(), True, DIRECTION_THRESHOLD),  # Front bounding line        
    ]

    # Add circular obstacle and bounding lines to obstacle list
    #obstacle_list += [CircularObstacle(collision_center[0], collision_center[1], collision_radius)] + bounding_lines
    obstacle_list += bounding_lines

    # Calculate X and Y distances
    shifted_points_x = [line.shifted_point[0] for line in bounding_lines]
    shifted_points_y = [line.shifted_point[1] for line in bounding_lines]

    X_DIST = (min(shifted_points_x), max(shifted_points_x))
    Y_DIST = (min(shifted_points_y), max(shifted_points_y))
    # ====Search Path with RRT====
    print(f"start RRT path planning for {vessel}")
    # Set Initial parameters
    rrt = BidirectionalRRTStarFND(
                    v_node=v_node,
                    start=vessel.p,
                    goal=goal,
                    min_go_around_line=min_go_around_line,
                    go_around_split_line=go_around_split_line,
                    sample_area=[X_DIST, Y_DIST],
                    obstacle_list=obstacle_list,
                    expand_dist=expand_distance,
                    goal_sample_rate=GOAL_SAMPLE_RATE,
                    collision_points=collision_points,
                    interpolator=interpolator,
                    scaler = SCALER * MAX_COORD / start_goal_dist / 1.5)
    
    # Add the original position to start the path
    path = rrt.plan_trajectory()
    
    return path, rrt.current_i, expand_distance
    

interpolator = PathInterpolator()

ordered_vessels = VesselOrderGraph(scenario.functional_scenario).sort()
        
# give_way_vessels_precedence = sorted(
#     list(give_way_vessels.values()),
#     key=lambda item: (len(item[1]), item[0].maneuverability())  # Sort firstly by the give-way numbers (how many corrections the vessel has to make) then by maneuverability (less maneuverable ships has to adapt to less other trajectories)
# )

start_time = datetime.now()
iter_numbers : Dict[int, int] = {}
eval_times : Dict[int, float] = {}
expand_distances : Dict[int, float] = {}
        
for v_node in ordered_vessels:
    o_start_time = datetime.now()
    
    vessel = scenario.to_concrete_vessel(v_node.vessel)
    path, iter_number, expand_distance = run_trajectory_generation(vessel, interpolator)  
    interpolator.add_path(vessel, path)
    
    o_eval_time = (datetime.now() - o_start_time).total_seconds()
    eval_times[v_node.vessel.id] = o_eval_time
    iter_numbers[v_node.vessel.id] = iter_number
    expand_distances[v_node.vessel.id] = expand_distance
    
overall_eval_time = (datetime.now() - start_time).total_seconds()
timestamp = datetime.now().isoformat()

traj_data = TrajectoryData(measurement_name=measurement_name, iter_numbers=iter_numbers, algorithm_desc='RRTStar_algo', 
                        config_name=eval_data.scenario_name, env_path=eval_data.path, random_seed=seed,
                        expand_distances=expand_distances, goal_sample_rate=GOAL_SAMPLE_RATE,
                        timestamp=timestamp, trajectories=interpolator.trajectories,
                        overall_eval_time=overall_eval_time, rrt_evaluation_times=eval_times)



asset_folder = f'{ASSET_FOLDER}/gen_data/{traj_data.algorithm_desc}/{traj_data.config_name}/{measurement_id}'
if not os.path.exists(asset_folder):
    os.makedirs(asset_folder)
file_path=f"{asset_folder}/{traj_data.timestamp.replace(':','-')}.json"
traj_data.path = file_path
traj_data.save_to_json(file_path=file_path)

ScenarioPlotManager(TrajectoryManager())
