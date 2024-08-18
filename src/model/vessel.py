import numpy as np
from model.usv_config import MIN_SPEED

class VesselDesc():
    def __init__(self, id: int, r: float, max_speed: float) -> None:
        self.id = id
        self.r = r
        self.max_speed = max_speed
        self.min_speed = MIN_SPEED
        
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselDesc) and
            self.id == value.id and self.r == value.r and
            self.max_speed == value.max_speed and
            self.min_speed == self.min_speed)

class Vessel():
    def __init__(self, desc: VesselDesc):
        self.id = desc.id
        self.r = desc.r
        self.max_speed = desc.max_speed
        self.min_speed = desc.min_speed
        self.update(0,0,0,0)  
        
    def update(self, p_x, p_y, v_x, v_y):
        self.p = np.array([p_x, p_y])
        self.v = np.array([v_x, v_y])
        self.speed = np.linalg.norm(self.v)        
  