import numpy as np

HEAD_ON_ANGLE = np.radians(20.0)
OVERTAKE_ANGLE =np.radians(140.0)
CROSSING_ANGLE = np.radians(100.0)
VISIBILITY_RANGE = 1852.001 # 6 neutical miles in metres

KNOT_CONVERSION = 0.5144447

MIN_SPEED = 1.0 * KNOT_CONVERSION # 1 knot in metres per second
MAX_SPEED = 40.0 * KNOT_CONVERSION
MIN_COORD = 0.0
def MAX_COORD(actor_num) -> float:
    return actor_num * 1000

def MAX_DISTANCE(actor_num) -> float:
    return (MAX_COORD(actor_num) - MIN_COORD) * np.sqrt(2)
MIN_VELOCITY_COORD = -MAX_SPEED
MAX_VELOCITY_COORD = MAX_SPEED

EPSILON=1e-10

CONSTRAINT_NUMBER = 4

def RANGE_FAR(actor_num) -> list[float]:
    return [VISIBILITY_RANGE, MAX_DISTANCE(actor_num)]

RANGE_VIS = [VISIBILITY_RANGE -20, VISIBILITY_RANGE + 20] # Around the visibility range with error threshold

def BOUNDARIES(actor_num) -> list[tuple[float, float]]:
    return [(MIN_COORD, MAX_COORD(actor_num)), (MIN_COORD, MAX_COORD(actor_num)),
              (MIN_VELOCITY_COORD, MAX_VELOCITY_COORD), (MIN_VELOCITY_COORD, MAX_VELOCITY_COORD)]
    
    
def angle(dot_product, norm_a, norm_b):
    norm_a = max(norm_a, EPSILON)
    norm_b = max(norm_b, EPSILON)
    cos_theta = dot_product / (norm_a * norm_b)
    cos_theta = np.clip(cos_theta, -1, 1)
    return np.arccos(cos_theta)

def interval_penalty(value, boundaries):
    minimum, maximum = boundaries
    if value < minimum:
        return minimum - value
    elif value > maximum:
        return value - maximum
    else:
        return 0.0

