from typing import Union
import numpy as np
import math
from concrete_level.models.actor_state import ActorState
from haversine import inverse_haversine, Direction, Unit

from utils.math_utils import calculate_heading

REFERENCE_POINT = np.array([57.760277, 16.678081])

def to_true_north(heading: float, unit : Union[Unit.DEGREES, Unit.RADIANS] = Unit.RADIANS) -> float:
    """
    Convert from trigonometric heading (0° = east, 90° = north, 180° = west, -90° = south)
    to true north heading (0° = north, 90° = east, 180° = south, 270° = west).
    """
    if unit == Unit.RADIANS:
        heading = math.degrees(heading)
        return math.radians((90 - heading) % 360)
    elif unit == Unit.DEGREES:
        return (90 - heading) % 360
    else:
        raise ValueError("Invalid unit. Use Unit.DEGREES or Unit.RADIANS.")
    

def from_true_north(true_north: float, unit: Union[Unit.DEGREES, Unit.RADIANS] = Unit.RADIANS) -> float:
    """
    Convert from true north heading (0° = north, 90° = east, 180° = south, 270° = west)
    to trigonometric heading (0° = east, 90° = north, 180° = west, -90° = south).
    """
    angle = math.degrees(true_north) if unit == Unit.RADIANS else true_north
    heading = (90 - angle) % 360
    if heading > 180:
        heading -= 360
    return math.radians(heading) if unit == Unit.RADIANS else heading
    

def true_north_heading(p1 : np.ndarray, p2 : np.ndarray, unit: Union[Unit.DEGREES, Unit.RADIANS] = Unit.RADIANS) -> float:
    p12 = p2 - p1
    heading = to_true_north(calculate_heading(p12[0], p12[1]))
    if unit == Unit.RADIANS:
        return heading
    elif unit == Unit.DEGREES:
        return math.degrees(heading)
    else:
        raise ValueError("Invalid unit. Use Unit.DEGREES or Unit.RADIANS.")

def coord_to_lat_long(p : np.ndarray) -> np.ndarray:
    """
    Convert local coordinate system (meters) to latitude and longitude.
    
    :param x_meters: Easting (meters from the reference point), p[0]
    :param y_meters: Northing (meters from the reference point), p[1]
    :param ref_lat: Reference latitude in decimal degrees, REFERENCE_POINT[0]
    :param ref_lon: Reference longitude in decimal degrees, REFERENCE_POINT[1]
    :return: Tuple (latitude, longitude) in decimal degrees
    """
    
    distance = (p[0]**2 + p[1]**2)**0.5
    if distance == 0:
        return REFERENCE_POINT
    bearing = to_true_north(calculate_heading(p[0], p[1]))
    point = inverse_haversine(REFERENCE_POINT, distance, bearing, unit=Unit.METERS)
    return np.array(point)
    
    # x_heading = to_true_north(calculate_heading(p[0], 0))
    # y_heading = to_true_north(calculate_heading(0, p[1]))
    # point_x = inverse_haversine(REFERENCE_POINT, p[0], x_heading, unit=Unit.METERS)
    # point_y = inverse_haversine(point_x, p[1], y_heading, unit=Unit.METERS)
       
    # return np.array(point_y)

def waypoint_from_state(state : ActorState) -> dict:
    lat_long = coord_to_lat_long(state.p)
    return {
        "altitude": 0,
        "latitude": lat_long[0],
        "longitude": lat_long[1],
        "rostype": "GeoPoint"
    }
