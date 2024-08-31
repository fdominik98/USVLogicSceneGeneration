from model.usv_config import MAX_COORD
from model.vessel import Vessel
from trajectory_planning.path_interpolator import PathInterpolator
from visualization.colreg_plot import ColregPlot
from visualization.data_parser import DataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment
from visualization.colreg_animation import ColregAnimation
import numpy as np
from trajectory_planning.bidirectionalRRTStarFND import CircularObstacle, RRTStarFND, DIM, LineObstacle

scaler = 1 / MAX_COORD  * DIM / 1.5

def find_center_and_radius(points_array):
    # Calculate the center (centroid) by averaging the coordinates
    center = np.mean(points_array, axis=0)
    # Calculate the radius as the maximum distance from the center to any point
    distances = np.linalg.norm(points_array - center, axis=1)
    radius = np.max(distances)
    return center, radius


dp = DataParser()
df, _ = dp.load_files()

if df.size == 0:
    exit(0)

config = USV_ENV_DESC_LIST[df['config_name'][0]]
env = USVEnvironment(config).update(df['best_solution'][0])
ColregPlot(env)

colreg_s = list(env.colreg_situations)[0]
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
]  # [x,y,size]
# Set Initial parameters
rrt = RRTStarFND(start=start,
                 goal=goal,
                randArea=[DIM, DIM],
                obstacleList=obstacleList,
                expandDis=10.0,
                goalSampleRate=15,
                maxIter=100)
path = rrt.Planning(animation=True)

path.reverse()
path = [np.array(pos) * (1.0 / scaler) for pos in path]

interpolator = PathInterpolator(o1, path)
interpolated_path = interpolator.interpolate_path()
print(interpolated_path)
