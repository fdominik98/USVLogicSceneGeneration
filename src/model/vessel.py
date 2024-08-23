import numpy as np
from model.usv_config import KNOT_TO_MS_CONVERSION, MAX_COORD

class VesselDesc():
    # r : meter
    # max_speed: knot
    def __init__(self, id: int, l: float, b: float, max_speed: float) -> None:
        self.id = id
        self.l = l
        self.b = b
        self.max_speed = max_speed * KNOT_TO_MS_CONVERSION
        
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselDesc) and
            self.id == value.id and self.l == value.l and
            self.max_speed == value.max_speed)

class Vessel():
    def __init__(self, desc: VesselDesc):
        self.id = desc.id
        self.l = desc.l
        self.b = desc.b
        self.max_speed = desc.max_speed
        
    def update(self, p_x, p_y, heading, speed):
        self.p = np.array([p_x, p_y])
        self.v = np.array([np.cos(heading), np.sin(heading)]) * speed
        self.speed = speed    
        self.heading = heading
        
    def v_norm(self):
        return self.v / self.speed
 