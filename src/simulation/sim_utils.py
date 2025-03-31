import numpy as np
import math

from concrete_level.models.actor_state import ActorState


REFERENCE_POINT = np.array([55.6590472, 17.3630944])

def to_true_north(heading: float) -> float:
    """
    Convert from trigonometric heading (0° = east, 90° = north, 180° = west, -90° = south)
    to true north heading (0° = north, 90° = east, 180° = south, 270° = west).
    """
    true_north = (90 - heading) % 360
    return true_north


def from_true_north(true_north: float) -> float:
    """
    Convert from true north heading (0° = north, 90° = east, 180° = south, 270° = west)
    to trigonometric heading (0° = east, 90° = north, 180° = west, -90° = south).
    """
    heading = (90 - true_north) % 360
    if heading > 180:
        heading -= 360  # Convert to range [-180, 180]
    return heading

def coord_to_lat_long(p : np.ndarray) -> np.ndarray:
    """
    Convert local coordinate system (meters) to latitude and longitude.
    
    :param x_meters: Easting (meters from the reference point), p[0]
    :param y_meters: Northing (meters from the reference point), p[1]
    :param ref_lat: Reference latitude in decimal degrees, REFERENCE_POINT[0]
    :param ref_lon: Reference longitude in decimal degrees, REFERENCE_POINT[1]
    :return: Tuple (latitude, longitude) in decimal degrees
    """
    # Approximate meters per degree at the reference latitude
    lat_offset = p[1] / 111320
    lon_offset = p[0] / 111320 * math.cos(math.radians(REFERENCE_POINT[0]))
    
    # Compute new lat and lon
    new_lat = REFERENCE_POINT[0] + lat_offset
    new_lon = REFERENCE_POINT[1] + lon_offset
    
    return np.array([new_lat, new_lon])

def waypoint_from_state(state : ActorState) -> dict:
    lat_long = coord_to_lat_long(state.p)
    return {
        "altitude": 0,
        "latitude": lat_long[0],
        "longitude": lat_long[1],
        "rostype": "GeoPoint"
    }
