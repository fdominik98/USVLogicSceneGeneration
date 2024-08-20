import numpy as np

HEAD_ON_ANGLE = np.radians(10.0)
OVERTAKE_ANGLE = np.radians(135)
CROSSING_ANGLE = np.radians(107.5)
MASTHEAD_ANGLE = HEAD_ON_ANGLE + 2 * CROSSING_ANGLE

KNOT_TO_MS_CONVERSION = 0.5144447
N_MILE_TO_M_CONVERSION = 1852.001 # a nautical miles in metres

DIST_DRIFT = 50.0

# 6 nautical miles = 11112,066 meters
# 5 nautical miles = 9260,005 meters
# 4 nautical miles = 7408,004 meters
# 3 nautical miles = 5556,003 meters
# 2 nautical miles = 3704,002 meters

MIN_SPEED = 0.0 * KNOT_TO_MS_CONVERSION # 1 knot in metres per second
MAX_SPEED = 45.0 * KNOT_TO_MS_CONVERSION
MIN_COORD = 0.0
MAX_COORD = 2 * 6 * N_MILE_TO_M_CONVERSION

EPSILON=1e-10

CONSTRAINT_NUMBER = 4
    
BOUNDARIES = [(MIN_COORD, MAX_COORD), (MIN_COORD, MAX_COORD),
              (-MAX_SPEED, MAX_SPEED), (-MAX_SPEED, MAX_SPEED)]
    
    
def angle(dot_product, norm_a, norm_b):
    norm_a = max(norm_a, EPSILON)
    norm_b = max(norm_b, EPSILON)
    cos_theta = dot_product / (norm_a * norm_b)
    cos_theta = np.clip(cos_theta, -1, 1)
    return np.arccos(cos_theta)

def interval_penalty(value : float, boundaries: tuple[float, float]):
    minimum, maximum = boundaries[0] + EPSILON, boundaries[1] - EPSILON # Penalize values on the edges as well
    if value < minimum:
        return minimum - value
    elif value > maximum:
        return value - maximum
    else:
        return 0.0
    
    
def o2VisibilityByo1(o2RelativeBearingToo1 : float, o2_radius):
    if o2RelativeBearingToo1 > MASTHEAD_ANGLE / 2:
        if o2_radius < 12:
            return 2
        elif o2_radius < 20:
            return 2
        elif o2_radius < 50:
            return 2
        else:
            return 3
    else:
        if o2_radius < 12:
            return 2
        elif o2_radius < 20:
            return 3
        elif o2_radius < 50:
            return 5
        else:
            return 6

