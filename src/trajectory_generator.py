from datetime import datetime
import os
import random
from typing import List, Tuple, Dict
from model.usv_config import MAX_COORD
from model.vessel import Vessel
from model.colreg_situation import ColregSituation, HeadOn, NoColreg
from trajectory_planning.trajectory_data import TrajectoryData
from trajectory_planning.path_interpolator import PathInterpolator
from visualization.colreg_plot import ColregPlot
from visualization.data_parser import EvalDataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment
import numpy as np
from trajectory_planning.bidirectionalRRTStarFND import CircularObstacle, Obstacle, RRTStarFND, DIM, LineObstacle

SCALER = 1 / MAX_COORD  * DIM * 2

DIRECTION_THRESHOLD = 50 # meter
EXPAND_DISTANCE = MAX_COORD / 120
GOAL_SAMPLE_RATE = 50.0 #%
MAX_ITER = 30000
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
ColregPlot(env)

def run_traj_generation(o : Vessel, colregs : List[ColregSituation]):
    if len(colregs) == 0:
        return [], 0
    
    obstacle_list : List[Obstacle] = []
    all_collision_points : List[np.ndarray] = []
    
    expand_distance = 1000 / o.maneuverability() 
    v_expand = o.v_norm() * expand_distance   
    start = o.p + v_expand
    
    for colreg_s in colregs:
        collision_points = colreg_s.get_colision_points(np.inf)
        all_collision_points.append(collision_points)
        #collision_center, collision_radius = find_center_and_radius(collision_points)          
    all_collision_points = np.concatenate(all_collision_points, axis=0)
        
    collision_center, collision_radius = find_center_and_radius(all_collision_points)
    
    goal = o.p + o.v_norm() * (np.linalg.norm(o.p - collision_center) + 3 * collision_radius) 
    
    # Define the bounding lines
    bounding_lines = [
        LineObstacle(o.p[0], o.p[1], o.v_norm(), True, DIRECTION_THRESHOLD),   # Left bounding line
        LineObstacle(goal[0], goal[1], o.v_norm(), False, collision_radius * 1.5), # Right bounding line
        LineObstacle(o.p[0], o.p[1], o.v_norm_perp(), False, DIRECTION_THRESHOLD), # Behind bounding line
        LineObstacle(goal[0], goal[1], o.v_norm_perp(), True, DIRECTION_THRESHOLD),  # Front bounding line        
    ]

    # Add circular obstacle and bounding lines to obstacle list
    obstacle_list += [CircularObstacle(collision_center[0], collision_center[1], collision_radius)] + bounding_lines

    # Calculate X and Y distances
    shifted_points_x = [line.shifted_point[0] for line in bounding_lines]
    shifted_points_y = [line.shifted_point[1] for line in bounding_lines]

    X_DIST = (min(shifted_points_x), max(shifted_points_x))
    Y_DIST = (min(shifted_points_y), max(shifted_points_y))
    # ====Search Path with RRT====
    print(f"start RRT path planning for {o}")
    # Set Initial parameters
    rrt = RRTStarFND(
                    vessel=o,
                    start=start,
                    goal=goal,
                    randArea=[X_DIST, Y_DIST],
                    obstacleList=obstacle_list,
                    expandDis=expand_distance,
                    goalSampleRate=GOAL_SAMPLE_RATE,
                    maxIter=MAX_ITER,
                    collision_points=all_collision_points,
                    scaler = SCALER)
    # Add the original position to start the path
    path = [o.p] + rrt.plan_trajectory(animation=True)
    # # Add a last sections to restore original path
    # for i in range(3):
    #     path += [goal + v_expand * (i + 1)]
    
    return path, rrt.current_i, expand_distance
    
    
    
interpolator = PathInterpolator(env)

give_way_vessels : Dict[int, Tuple[Vessel, List[ColregSituation]]] = {o.id : (o, []) for o in env.vessels}

for colreg_s in env.colreg_situations:
    if isinstance(colreg_s, NoColreg):
        continue
    give_way_vessels[colreg_s.vessel1.id][1].append(colreg_s)
    if isinstance(colreg_s, HeadOn):
        give_way_vessels[colreg_s.vessel2.id][1].append(colreg_s)
    
        
give_way_vessels_precedence = sorted(
    list(give_way_vessels.values()),
    key=lambda item: (len(item[1]), item[0].maneuverability())  # Sort firstly by the give-way numbers (how many corrections the vessel has to make) then by maneuverability (less maneuverable ships has to adapt to less other trajectories)
)

start_time = datetime.now()
iter_numbers : Dict[int, int] = {}
eval_times : Dict[int, float] = {}
expand_distances : Dict[int, float] = {}
        
for o, colregs in give_way_vessels_precedence:
    o_start_time = datetime.now()
    
    path, iter_number, expand_distance = run_traj_generation(o, colreg_s)  
    interpolator.add_path(o, path)
    
    o_eval_time = (datetime.now() - o_start_time).total_seconds()
    eval_times[o.id] = o_eval_time
    iter_numbers[o.id] = iter_number
    expand_distances[o.id] = expand_distance
    
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

ColregPlot(env, trajectories=traj_data.trajectories)
