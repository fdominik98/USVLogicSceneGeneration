import numpy as np
from model.usv_config import *

class Vessel():
    def __init__(self, id : int, r : float):
        self.id = id
        self.r = r
        self.update(0,0,0,0)  
        
    def update(self, p_x, p_y, v_x, v_y):
        self.p = np.array([p_x, p_y])
        self.v = np.array([v_x, v_y])
        self.speed = np.linalg.norm(self.v)
        
    def __eq__(self, value: object) -> bool:
        return isinstance(value, Vessel) and self.id == value.id and self.r == value.r and self.p == value.p and self.v == value.v