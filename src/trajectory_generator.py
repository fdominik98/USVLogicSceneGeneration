from datetime import datetime
import os
import random
from model.usv_config import MAX_COORD
from model.vessel import Vessel
from model.colreg_situation import HeadOn
from trajectory_planning.trajectory_data import TrajectoryData
from trajectory_planning.path_interpolator import PathInterpolator
from visualization.colreg_plot import ColregPlot
from visualization.data_parser import EvalDataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment
import numpy as np
from trajectory_planning.bidirectionalRRTStarFND import CircularObstacle, RRTStarFND, DIM, LineObstacle

scaler = 1 / MAX_COORD  * DIM / 1.2

DIRECTION_THRESHOLD = 1
AREA = 2 * MAX_COORD
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

interpolator = PathInterpolator(env.vessels, EXPAND_DISTANCE)

start_time = datetime.now()
iter_numbers : dict[str, tuple[int, int]] = {}
eval_times : dict[str, tuple[float, float]] = {}


def run_traj_generation(o : Vessel, collision_center : np.ndarray, collision_radius : float):
    p_scaled = o.p * scaler
    v_expand_scaled = o.v_norm() * EXPAND_DISTANCE * scaler
    start = p_scaled + v_expand_scaled
    goal = p_scaled + o.v_norm() * (np.linalg.norm(p_scaled - collision_center) + 3 * collision_radius) 

    print("start RRT path planning for o")

    # ====Search Path with RRT====
    obstacleList = [
        CircularObstacle(collision_center[0], collision_center[1], collision_radius),
        LineObstacle(p_scaled[0], p_scaled[1], o.v_norm(), True, DIRECTION_THRESHOLD),
        LineObstacle(p_scaled[0], p_scaled[1], o.v_norm_perp(), False, DIRECTION_THRESHOLD),
        LineObstacle(goal[0], goal[1], o.v_norm_perp(), True, DIRECTION_THRESHOLD),
        LineObstacle(p_scaled[0], p_scaled[1], o.v_norm(), False, collision_radius * 1.5)
    ]
    # Set Initial parameters
    rrt = RRTStarFND(start=start,
                    goal=goal,
                    randArea=[AREA * scaler, AREA * scaler],
                    obstacleList=obstacleList,
                    expandDis=EXPAND_DISTANCE * scaler,
                    goalSampleRate=GOAL_SAMPLE_RATE,
                    maxIter=MAX_ITER)
    # Add the original position to start the path
    path = [p_scaled] + rrt.Planning(animation=True)
    # Add a last sections to restore original path
    for i in range(3):
        path += [goal + v_expand_scaled * (i + 1)]
    path = [np.array(pos) * (1.0 / scaler) for pos in path]
    
    return path, rrt.current_i
        
        
for colreg_s in env.colreg_situations:
    
    o1 = env.vessels[0]
    o2 = env.vessels[1]

    colision_points = colreg_s.get_colision_points(np.inf)
    center, radius = find_center_and_radius(colision_points)

    center = center * scaler
    radius = radius * 3 * scaler
    
    o1_start_time = datetime.now()
    path1, iter_number1 = run_traj_generation(o1, center, radius)
    o1_eval_time = (datetime.now() - o1_start_time).total_seconds()
    interpolator.add_path(o1, path1)
    
    if isinstance(colreg_s, HeadOn):
        o2_start_time = datetime.now()
        path2, iter_number2 = run_traj_generation(o2, center, radius)
        o2_eval_time = (datetime.now() - o2_start_time).total_seconds()
    else:
        path2, iter_number2 = [], 0
        o2_eval_time = 0
    interpolator.add_path(o2, path2)
    
    eval_times[colreg_s.name] = (o1_eval_time, o2_eval_time)
    iter_numbers[colreg_s.name] = (iter_number1, iter_number2)
    
        
 
interpolator.interpolate()
overall_eval_time = (datetime.now() - start_time).total_seconds()
timestamp = datetime.now().isoformat()

traj_data = TrajectoryData(measurement_name=measurement_name, iter_numbers=iter_numbers, algorithm_desc='RRTStar_algo', 
                        config_name=data.config_name, env_path=data.path, random_seed=seed,
                        expand_distance=EXPAND_DISTANCE, goal_sample_rate=GOAL_SAMPLE_RATE,
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
