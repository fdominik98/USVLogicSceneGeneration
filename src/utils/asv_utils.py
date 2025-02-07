import numpy as np

BOW_ANGLE = np.radians(10.0)
STERN_ANGLE = np.radians(135)
BEAM_ANGLE = np.radians(107.5)
MASTHEAD_LIGHT_ANGLE = np.pi * 2 - STERN_ANGLE

KNOT_TO_MS_CONVERSION = 0.5144447 # 1 knot in metres per second
N_MILE_TO_M_CONVERSION = 1852.001 # 1 nautical miles in metres

DIST_DRIFT = 50.0

# 6 nautical miles = 11112,066 meters
# 5 nautical miles = 9260,005 meters
# 4 nautical miles = 7408,004 meters
# 3 nautical miles = 5556,003 meters
# 2 nautical miles = 3704,002 meters

MIN_HEADING = -np.pi
MAX_HEADING = np.pi
MIN_COORD = 0.0
MAX_COORD = 2 * 6.5 * N_MILE_TO_M_CONVERSION # 24076.013 m
MAX_DISTANCE = MAX_COORD * np.sqrt(2) # 34048.624 m

EPSILON=1e-10

MIN_LENGTH = 10
MAX_LENGTH = 400
MIN_BEAM = 2
MAX_BEAM = 80
MIN_SPEED_IN_MS = 0.2 * KNOT_TO_MS_CONVERSION
MAX_SPEED_IN_MS = 50 * KNOT_TO_MS_CONVERSION

EGO_LENGTH = 30
EGO_BEAM = 10

ONE_HOUR_IN_SEC = 60 * 60
TWO_N_MILE = 2 * N_MILE_TO_M_CONVERSION

def vessel_radius(length : float) -> float:
    return length * 4

def o2VisibilityByo1(o2RelativeBearingToo1 : float, o2_length):
    if o2RelativeBearingToo1 >= MASTHEAD_LIGHT_ANGLE / 2:
        if o2_length < 12:
            return 2
        elif o2_length < 20:
            return 2
        elif o2_length < 50:
            return 2
        else:
            return 3
    else:
        if o2_length < 12:
            return 2
        elif o2_length < 20:
            return 3
        elif o2_length < 50:
            return 5
        else:
            return 6
        

# FOR FUTURE WORK
# Table 1: Approximated minimum spacing for Coldwell's domain if ownship's length and beam are L1 and B1, and target's length and beam are L2 and B2, respectively.

# Encounter/Safety Condition                      | Own Domain Not Violated | Target's Domain Not Violated | Neither Domain is Violated | Domains Not Overlapping
# ---------------------------------------------------------------------------------------------------------------------------
# Head-on (port to a target)                      | 1.75L1 - 0.5B1          | 1.75L2 - 0.5B2              | 1.75L2 - 0.5B2            | 1.75L1 - 0.5B1 + 1.75L2 - 0.5B2
# Head-on (starboard to a target)                 | 3.25L1 - 0.5B1          | 3.25L2 - 0.5B2              | 3.25L2 - 0.5B2            | 3.25L1 - 0.5B1 + 3.25L2 - 0.5B2
# Crossing ahead of a target on starboard         | 3.25L1 - 0.5B1          | 6.1L2 - 0.5L2               | 6.1L2 - 0.5L2             | 3.25L1 - 0.5B1 + 6.1L2 - 0.5L2
# Crossing astern of a target from starboard      | 1.75L1 - 0.5B1          | 3.9L2 - 0.5L2               | 3.9L2 - 0.5L2             | 1.75L1 - 0.5B1 + 3.9L2 - 0.5L2
# Crossing ahead of a target on port              | 1.75L1 - 0.5B1          | 6.1L2 - 0.5L2               | 6.1L2 - 0.5L2             | 1.75L1 - 0.5B1 + 6.1L2 - 0.5L2
# Crossing astern of a target from port           | 3.25L1 - 0.5B1          | 3.9L2 - 0.5L2               | 3.9L2 - 0.5L2             | 3.25L1 - 0.5B1 + 3.9L2 - 0.5L2
# Overtaking (port to a target or starboard)      | 1.75L1 - 0.5B1          | 1.75L2 - 0.5B2              | 1.75L2 - 0.5B2            | 1.75L1 - 0.5B1 + 1.75L2 - 0.5B2

