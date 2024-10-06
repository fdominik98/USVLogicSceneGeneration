import numpy as np
from model.environment.usv_config import KNOT_TO_MS_CONVERSION

class VesselDesc():
    # r : meter
    # max_speed: knot
    def __init__(self, id: int, l: float, b: float, max_speed: float, min_speed : float = 1.0) -> None:
        self.id = id
        self.l = l
        self.b = b
        self.max_speed = max_speed * KNOT_TO_MS_CONVERSION
        self.min_speed = min_speed * KNOT_TO_MS_CONVERSION
        self.name = r'OS' if self.id == 0 else fr'$TS_{self.id}$'
        
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselDesc) and
            self.id == value.id and self.l == value.l and
            self.max_speed == value.max_speed)
        
    def __repr__(self) -> str:
        return self.name + ' desc'

class Vessel():
    def __init__(self, desc: VesselDesc):
        self.id = desc.id
        self.l = desc.l
        self.r = desc.l * 2.0
        self.name = desc.name
        self.max_speed = desc.max_speed
        
    def update(self, p_x, p_y, heading, speed) -> None:
        self.p = np.array([p_x, p_y])
        self.v = np.array([np.cos(heading), np.sin(heading)]) * speed
        self.speed = speed    
        self.heading = heading
        
    def v_norm(self) -> np.ndarray:
        return self.v / self.speed
    
    def v_norm_perp(self) -> np.ndarray:
        v_norm = self.v_norm()
        return np.array([v_norm[1], -v_norm[0]])
    
    def maneuverability(self) -> float:
        return 9.81 / (9.81 * self.l + self.speed * self.speed)
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    
    def is_OS(self):
        return self.id == 0
    
 