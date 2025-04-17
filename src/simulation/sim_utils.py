from typing import Union
import numpy as np
import math
from concrete_level.models.actor_state import ActorState
from haversine import inverse_haversine, Direction, Unit

from utils.math_utils import calculate_heading

REFERENCE_POINT = np.array([55.6590472, 17.3630944])

def to_true_north(heading: float, unit : Union[Unit.DEGREES, Unit.RADIANS] = Unit.RADIANS) -> float:
    """
    Convert from trigonometric heading (0° = east, 90° = north, 180° = west, -90° = south)
    to true north heading (0° = north, 90° = east, 180° = south, 270° = west).
    """
    if unit == Unit.RADIANS:
        heading = math.degrees(heading)
    elif unit == Unit.DEGREES:
        pass
    else:
        raise ValueError("Invalid unit. Use Unit.DEGREES or Unit.RADIANS.")
    # Convert to true north heading
    true_north = (90 - heading) % 360
    return true_north

def from_true_north(true_north: float, unit : Union[Unit.DEGREES, Unit.RADIANS] = Unit.RADIANS) -> float:
    """
    Convert from true north heading (0° = north, 90° = east, 180° = south, 270° = west)
    to trigonometric heading (0° = east, 90° = north, 180° = west, -90° = south).
    """
    if unit == Unit.RADIANS:
        true_north = math.degrees(true_north)
    elif unit == Unit.DEGREES:
        pass
    else:
        raise ValueError("Invalid unit. Use Unit.DEGREES or Unit.RADIANS.")
    
    heading = (90 - true_north) % 360
    if heading > 180:
        heading -= 360  # Convert to range [-180, 180]
    return heading

from math import atan2, radians, degrees, sin, cos

def true_north_heading(p1 : np.ndarray, p2 : np.ndarray) -> float:
    delta_lon = p1[1] - p2[1]
    x = sin(delta_lon) * cos(p1[0])
    y = cos(p2[0]) * sin(p1[0]) - sin(p2[0]) * cos(p1[0]) * cos(delta_lon)
    
    initial_bearing = atan2(x, y)
    # Convert to degrees and normalize
    bearing_degrees = (degrees(initial_bearing) + 360) % 360
    return bearing_degrees

def coord_to_lat_long(p : np.ndarray) -> np.ndarray:
    """
    Convert local coordinate system (meters) to latitude and longitude.
    
    :param x_meters: Easting (meters from the reference point), p[0]
    :param y_meters: Northing (meters from the reference point), p[1]
    :param ref_lat: Reference latitude in decimal degrees, REFERENCE_POINT[0]
    :param ref_lon: Reference longitude in decimal degrees, REFERENCE_POINT[1]
    :return: Tuple (latitude, longitude) in decimal degrees
    """
    
    x_heading = to_true_north(calculate_heading(p[0], 0))
    y_heading = to_true_north(calculate_heading(0, p[1]))
    point_x = inverse_haversine(REFERENCE_POINT, p[0], x_heading, unit=Unit.METERS)
    point_y = inverse_haversine(point_x, p[1], y_heading, unit=Unit.METERS)
    
    # # Approximate meters per degree at the reference latitude
    # lat_offset = p[1] / 111320
    # lon_offset = p[0] / 111320 * math.cos(math.radians(REFERENCE_POINT[0]))
    
    # # Compute new lat and lon
    # new_lat = REFERENCE_POINT[0] + lat_offset
    # new_lon = REFERENCE_POINT[1] + lon_offset
    
    return np.array(point_y)

def waypoint_from_state(state : ActorState) -> dict:
    lat_long = coord_to_lat_long(state.p)
    return {
        "altitude": 0,
        "latitude": lat_long[0],
        "longitude": lat_long[1],
        "rostype": "GeoPoint"
    }
