from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np
from model.vessel import Vessel

class Node():
    """
    RRT Node
    """
    def __init__(self, p : np.ndarray):
        self.p = p
        self.distance_cost = 0.0
        self.time_cost : int = 0
        self.s_fraction = False
        self.parent : Optional[int] = None
        self.children : set[int] = set()
        
    @staticmethod
    def calc_cost(vessel : Vessel, d : float) -> Tuple[int, bool]:
        # Calculate the distance and heading between the points
        s_dist = int(d // vessel.speed)
        # Calculate the number of seconds required to cover the distance
        s_fraction = d / vessel.speed - s_dist
        if s_fraction > 0.0001:
            return s_dist + 1, True 
        return s_dist, False
    
    def set_cost(self, d : float, time : int, fraction : bool):
        self.distance_cost = d
        self.time_cost = time
        self.s_fraction = fraction       
        
class Obstacle(ABC):
    MARGIN = 0.02
    def __init__(self, x : float, y : float) -> None:
        super().__init__()
        self.p = np.array([x, y])
        
    @abstractmethod    
    def check_no_collision(self, node : Node) -> bool:
        pass
  
    
class CircularObstacle(Obstacle):
    def __init__(self, x : float, y : float, radius : float) -> None:
        super().__init__(x, y)
        self.radius = radius
        
    def check_no_collision(self, node : Node) -> bool:
        d = np.linalg.norm(node.p - self.p)
        if d <= self.radius + self.radius * self.MARGIN:
            return False  # collision
        return True  # safe
    
    
class LineObstacle(Obstacle):
    def __init__(self, x : float, y : float, dir_vec : np.ndarray, above_initial_point : bool, shift) -> None:
        super().__init__(x, y)
        self.shift = shift
        self.dir_vec = dir_vec
        self.above_initial_point = above_initial_point
        if above_initial_point:
            perpendicular = np.array([-dir_vec[1], dir_vec[0]])
        else:
            perpendicular = np.array([dir_vec[1], -dir_vec[0]])
            
        # Normalize the perpendicular vector
        self.perpendicular = perpendicular / np.linalg.norm(perpendicular)

        # Compute the shifted point on the line
        self.shifted_point = self.p + self.shift * self.perpendicular

        
    def check_no_collision(self, node : Node) -> bool:
        # Compute the cross product to determine the position relative to the shifted line
        # Line equation is implicit: (P - shifted_point) dotted with the perpendicular vector should be checked
        position_value = np.dot(self.perpendicular, node.p - self.shifted_point)

        if self.above_initial_point:
            if position_value > 0:
                return False # collision
            else:
                return True # safe
        else:
            if position_value < 0:
                return True # collision
            else:
                return False # safe
        # Determine if point is above or below the shifted line