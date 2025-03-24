import numpy as np
import math

from concrete_level.models.vessel_state import ActorState


REFERENCE_POINT = np.array([57.75425, 16.77096])

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
    meters_per_degree_lat = 111320
    meters_per_degree_lon = 111320 * math.cos(math.radians(REFERENCE_POINT[0]))
    
    # Compute new lat and lon
    new_lat = REFERENCE_POINT[0] + (p[1] / meters_per_degree_lat)
    new_lon = REFERENCE_POINT[1] + (p[0] / meters_per_degree_lon)
    
    return np.array([new_lat, new_lon])

def waypoint_from_state(state : ActorState) -> dict:
    lat_long = coord_to_lat_long(state.p)
    return {
        "altitude": 0,
        "latitude": lat_long[0],
        "longitude": lat_long[1],
        "rostype": "GeoPoint"
    }
