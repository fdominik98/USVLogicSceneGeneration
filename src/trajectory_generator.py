from datetime import datetime
import os
import random
from model.usv_config import MAX_COORD
from model.vessel import Vessel
from trajectory_planning.trajectory_data import TrajectoryData
from trajectory_planning.path_interpolator import PathInterpolator
from visualization.colreg_plot import ColregPlot
from visualization.data_parser import EvalDataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment
from visualization.colreg_animation import ColregAnimation
import numpy as np
from trajectory_planning.bidirectionalRRTStarFND import CircularObstacle, RRTStarFND, DIM, LineObstacle

scaler = 1 / MAX_COORD  * DIM / 1.2
expand_distance = MAX_COORD / 100
goal_sample_rate = 50.0
maxIter = 1000
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
df, _ = dp.load_df()

if df.size == 0:
    exit(0)

data = df.loc[0]

config = USV_ENV_DESC_LIST[data['config_name']]
env = USVEnvironment(config).update(data['best_solution'])
ColregPlot(env)
interpolator = PathInterpolator(env.vessels)

start_time = datetime.now()

iter_numbers : dict[str, tuple[int, int]] = {}
eval_times : dict[str, tuple[float, float]] = {}

for colreg_s in env.colreg_situations:
    colreg_start_time = datetime.now()
    o1 = env.vessels[0]
    o2 = env.vessels[1]

    colision_points = colreg_s.get_colision_points(np.inf)
    center, radius = find_center_and_radius(colision_points)

    center = center * scaler
    radius = radius * scaler * 2
    start = (o1.p + o1.v) * scaler
    goal = start + o1.v_norm() * (np.linalg.norm(start-center) + 2 * radius) 

    o1p_scaled = o1.p * scaler
    print("start RRT path planning")

    # ====Search Path with RRT====
    obstacleList = [
        CircularObstacle(center[0], center[1], radius),
        LineObstacle(o1p_scaled[0], o1p_scaled[1], o1.v_norm(), True, 20),
        LineObstacle(o1p_scaled[0], o1p_scaled[1], o1.v_norm(), False, radius * 2)
    ]
    # Set Initial parameters
    rrt = RRTStarFND(start=start,
                    goal=goal,
                    randArea=[DIM, DIM],
                    obstacleList=obstacleList,
                    expandDis=expand_distance * scaler,
                    goalSampleRate=goal_sample_rate,
                    maxIter=maxIter)
    path = rrt.Planning(animation=True)
    path = [np.array(pos) * (1.0 / scaler) for pos in path]
    
    interpolator.add_path(o1, path)
    interpolator.add_path(o2, [])
    
    eval_times[colreg_s.name] = ((datetime.now() - colreg_start_time).total_seconds(), 0.0)
    iter_numbers[colreg_s.name] = (rrt.current_i, 0)


interpolator.interpolate()
overall_eval_time = (datetime.now() - start_time).total_seconds()
timestamp = datetime.now().isoformat()

traj_data = TrajectoryData(measurement_name=measurement_name, iter_numbers=iter_numbers, algorithm_desc='RRTStar_algo', 
                        config_name=data['config_name'], env_path=data['path'], random_seed=seed,
                        expand_distance=expand_distance, goal_sample_rate=goal_sample_rate,
                        max_iter=maxIter, timestamp=timestamp, trajectories=interpolator.interpolated_paths,
                        overall_eval_time=overall_eval_time, rrt_evaluation_times=eval_times)


current_file_directory = os.path.dirname(os.path.abspath(__file__))

asset_folder = f'{current_file_directory}/../assets/{traj_data.algorithm_desc}/{traj_data.config_name}/{measurement_id}'
if not os.path.exists(asset_folder):
    os.makedirs(asset_folder)
file_path=f"{asset_folder}/{traj_data.timestamp.replace(':','-')}.json"
traj_data.path = file_path
traj_data.save_to_json(file_path=file_path)
