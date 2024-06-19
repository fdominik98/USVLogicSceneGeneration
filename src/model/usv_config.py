import numpy as np
import math

head_on_angle = np.radians(30.0)
overtake_angle =np.radians(120.0)
crossing_angle = np.radians(90)
visibility_range = 1852.001 # 6 neutical miles in metres

speed_min = 5.0 * 0.5144447 # 5 knots in metres per second
speed_max = 40.0 * 0.5144447
point_min = 0.0
point_max = 3500.0
max_distance = (point_max - point_min) * np.sqrt(2)
velocity_min = -speed_max
velocity_max = speed_max

epsilon=1e-10

constraint_number = 4

boundaries = [(point_min, point_max), (point_min, point_max),
              (velocity_min, velocity_max), (velocity_min, velocity_max)]

def interval_penalty(value, boundaries):
    minimum, maximum = boundaries
    if value < minimum:
        return minimum - value
    elif value > maximum:
        return value - maximum
    else:
        return 0.0    
    
def angle_norm(angle_diff):
    return linear_to_exponential(angle_diff / np.pi)

def distance_norm(distance_diff, boundaries):
    if distance_diff == 0.0:
        return 0.0
    max_diff = max(boundaries[0], (max_distance - boundaries[1]))
    return linear_to_exponential(distance_diff / max_diff)


def linear_to_exponential(x, base=math.e):
    k = 0.5 # steepness factor
    return (base ** (k * x) - 1) / (base ** k - 1)

    
def penalties_norm(penalties, distance):
    if len(penalties) != constraint_number:
        raise Exception(f'Only {len(penalties)} penalties instead of {constraint_number}')
    return [distance_norm(penalties[0], distance),
            angle_norm(penalties[1]),
            angle_norm(penalties[2]),
            angle_norm(penalties[3])]