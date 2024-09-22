from datetime import datetime
import os
import random
from typing import List, Dict
from model.usv_config import MAX_COORD
from visualization.colreg_plot_manager import ColregPlotManager
from trajectory_planning.rrt_utils import Obstacle, PolygonalObstacle, LineObstacle, CircularObstacle
from trajectory_planning.vessel_order_graph import VesselNode, VesselOrderGraph
from trajectory_planning.trajectory_data import TrajectoryData
from trajectory_planning.path_interpolator import PathInterpolator
from visualization.data_parser import EvalDataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment
import numpy as np
from trajectory_planning.bidirectionalRRTStarFND import RRTStarFND, DIM

SCALER = 1 / MAX_COORD  * DIM

DIRECTION_THRESHOLD = 100 # meter
GOAL_SAMPLE_RATE = 20.0 #%
MAX_ITER = np.inf
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

data = data_models[0]

config = USV_ENV_DESC_LIST[data.config_name]
env = USVEnvironment(config).update(data.best_solution)
ColregPlotManager(env)

def run_traj_generation(v_node : VesselNode, interpolator : PathInterpolator):
    o = v_node.vessel
    print(f'Calculation {o}:')
    expand_distance = o.speed * 60 # 1 minute precision
    
    if len(v_node.colreg_situations) == 0:
        return [], 0, expand_distance
    
    obstacle_list : List[Obstacle] = []
    collision_points : List[np.ndarray] = []    
    
    for colreg_s in v_node.colreg_situations:
        print(f'Collision points for static colreg {colreg_s}')
        colreg_collision_points = colreg_s.get_collision_points()
        collision_points += colreg_collision_points
    #colreg_collision_center, colreg_collision_radius = find_center_and_radius(colreg_collision_points)
   
    for id, path in interpolator.interpolated_paths.items():
        vessel = env.get_vessel_by_id(id)
        for i in range(interpolator.path_length):
            new_pos = o.p + i * o.v
            if np.linalg.norm(new_pos - np.array([path[i][0], path[i][1]])) < o.r + vessel.r:
                collision_points.append(new_pos)   
        
    if len(collision_points) != 0:
        collision_center, collision_radius = find_center_and_radius(collision_points)
    else:
        collision_center, collision_radius = o.p + o.v * interpolator.path_length / 2, 0
    
    start_coll_center_dist = np.linalg.norm(o.p - collision_center)
    start_goal_dist = start_coll_center_dist + max(start_coll_center_dist, collision_radius * 3)
    goal_vector = o.v_norm() * start_goal_dist
    goal = o.p + goal_vector
    poly_p1 = o.p + goal_vector / 4
    poly_p2 = o.p + goal_vector / 4 * 3
    poly_p3 = poly_p2 + o.v_norm_perp() * max(start_coll_center_dist, collision_radius * 4)
    poly_p4 = poly_p1 + o.v_norm_perp() * max(start_coll_center_dist, collision_radius * 4)
    #obstacle_list += [PolygonalObstacle(p1=poly_p1, p2=poly_p2, p3=poly_p3, p4=poly_p4)]
    obstacle_list += [CircularObstacle(collision_center, collision_radius)]
    
    # Define the bounding lines
    bounding_lines = [
        LineObstacle(o.p[0], o.p[1], o.v_norm(), True, DIRECTION_THRESHOLD),   # Left bounding line
        LineObstacle(goal[0], goal[1], o.v_norm(), False, max(start_coll_center_dist, collision_radius * 8)), # Right bounding line
        LineObstacle(o.p[0], o.p[1], o.v_norm(), False, max(start_coll_center_dist, collision_radius * 8    )), # Right bounding line
        LineObstacle(o.p[0], o.p[1], o.v_norm_perp(), False, DIRECTION_THRESHOLD), # Behind bounding line
        LineObstacle(goal[0], goal[1], o.v_norm_perp(), True, DIRECTION_THRESHOLD),  # Front bounding line        
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
    print(f"start RRT path planning for {o}")
    # Set Initial parameters
    rrt = RRTStarFND(
                    v_node=v_node,
                    start=o.p,
                    goal=goal,
                    sample_area=[X_DIST, Y_DIST],
                    obstacle_list=obstacle_list,
                    expand_dist=expand_distance,
                    goal_sample_rate=GOAL_SAMPLE_RATE,
                    max_iter=MAX_ITER,
                    collision_points=collision_points,
                    interpolator=interpolator,
                    scaler = SCALER * MAX_COORD / start_goal_dist / 1.5)
    # Add the original position to start the path
    path = rrt.plan_trajectory()
    
    return path, rrt.current_i, expand_distance
    

interpolator = PathInterpolator()

ordered_vessels = VesselOrderGraph(env.colreg_situations).sort()
        
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
    
    path, iter_number, expand_distance = run_traj_generation(v_node, interpolator)  
    interpolator.add_path(v_node.vessel, path)
    
    o_eval_time = (datetime.now() - o_start_time).total_seconds()
    eval_times[v_node.vessel.id] = o_eval_time
    iter_numbers[v_node.vessel.id] = iter_number
    expand_distances[v_node.vessel.id] = expand_distance
    
overall_eval_time = (datetime.now() - start_time).total_seconds()
timestamp = datetime.now().isoformat()

traj_data = TrajectoryData(measurement_name=measurement_name, iter_numbers=iter_numbers, algorithm_desc='RRTStar_algo', 
                        config_name=data.config_name, env_path=data.path, random_seed=seed,
                        expand_distances=expand_distances, goal_sample_rate=GOAL_SAMPLE_RATE,
                        max_iter=MAX_ITER, timestamp=timestamp, trajectories=interpolator.interpolated_paths,
                        overall_eval_time=overall_eval_time, rrt_evaluation_times=eval_times)


current_file_directory = os.path.dirname(os.path.abspath(__file__))

asset_folder = f'{current_file_directory}/../assets/gen_data/{traj_data.algorithm_desc}/{traj_data.config_name}/{measurement_id}'
if not os.path.exists(asset_folder):
    os.makedirs(asset_folder)
file_path=f"{asset_folder}/{traj_data.timestamp.replace(':','-')}.json"
traj_data.path = file_path
traj_data.save_to_json(file_path=file_path)

ColregPlotManager(env, trajectories=traj_data.trajectories)
