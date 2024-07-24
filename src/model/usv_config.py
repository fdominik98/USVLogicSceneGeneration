import numpy as np
import math

head_on_angle = np.radians(20.0)
overtake_angle =np.radians(140.0)
crossing_angle = np.radians(100.0)
visibility_range = 1852.001 # 6 neutical miles in metres

speed_min = 5.0 * 0.5144447 # 5 knots in metres per second
speed_max = 40.0 * 0.5144447
point_min = 0.0
def point_max(actor_num) -> float:
    return actor_num * 1000

def max_distance(actor_num) -> float:
    return (point_max(actor_num) - point_min) * np.sqrt(2)
velocity_min = -speed_max
velocity_max = speed_max

epsilon=1e-10

constraint_number = 3

def range_far(actor_num) -> list[float]:
    return [visibility_range, max_distance(actor_num)]

range_vis = [visibility_range, visibility_range + 100] # Around the visibility range with error threshold

def boundaries(actor_num) -> list[tuple[float, float]]:
    return [(point_min, point_max(actor_num)), (point_min, point_max(actor_num)),
              (velocity_min, velocity_max), (velocity_min, velocity_max)]

