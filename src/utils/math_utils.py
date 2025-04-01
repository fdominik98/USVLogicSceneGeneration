import numpy as np


def find_center_and_radius(points_array):
    # Calculate the center (centroid) by averaging the coordinates
    center = np.mean(points_array, axis=0)
    # Calculate the radius as the maximum distance from the center to any point
    distances = np.linalg.norm(points_array - center, axis=1)
    radius = np.max(distances)
    return center, radius


def compute_angle(vec1, vec2, norm1, norm2):
    """Compute angle between two vectors."""
    cos_theta = np.clip(np.dot(vec1, vec2) / (norm1 * norm2), -1, 1)
    return np.arccos(cos_theta)


def calculate_heading(vx : float, vy : float):
    heading_radians = np.arctan2(vy, vx)
    return heading_radians
