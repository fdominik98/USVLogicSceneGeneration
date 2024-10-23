from abc import ABC
import copy
import numpy as np
from model.environment.usv_config import EPSILON, KNOT_TO_MS_CONVERSION


class VesselDesc(ABC):
    max_speed = 30 * KNOT_TO_MS_CONVERSION # kn
    min_speed = 2 * KNOT_TO_MS_CONVERSION
    max_length = 100 # m
    min_length = 10
        
    def __init__(self, id : int):
        super().__init__()
        self.id = id
        
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselDesc) and
            self.id == value.id and            
            self.max_speed == value.max_speed and
            self.min_speed == value.min_speed and
            self.max_length == value.max_length and
            self.min_length == value.min_length)
        
    def __repr__(self) -> str:
        return 'desc'
    
    def __hash__(self):
        return hash((self.id, self.max_speed, self.min_speed, self.max_length, self.min_length, 'vessel description'))
    
    def is_OS(self):
        return isinstance(self, OS)
    

class OS(VesselDesc):
    max_length = 30 + EPSILON # m
    min_length = 30 - EPSILON
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, OS) and super().__eq__(value))
        
    def __repr__(self) -> str:
        return f'OS{self.id}'
    
    def __hash__(self):
        return hash((super().__hash__(), 'OS'))
    
class TS(VesselDesc):
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, TS) and super().__eq__(value))
        
    def __repr__(self) -> str:
        return f'TS{self.id}'
    
    def __hash__(self):
        return hash((super().__hash__(), 'TS'))


class VesselDescBig(VesselDesc, ABC):
    max_speed = 3000 * KNOT_TO_MS_CONVERSION # kn
    min_speed = 2500 * KNOT_TO_MS_CONVERSION
    max_length = 600 # m
    min_length = 600
    
class OSBig(OS, VesselDescBig):
    max_length = 400 # m
    min_length = 400
class TSBig(TS, VesselDescBig):
    pass
    
class Vessel():
    def __init__(self, desc: VesselDesc):
        self.desc = desc
        self.id = desc.id
        self.name = r'OS' if self.is_OS() else fr'$TS_{self.id}$'
        self.max_speed = desc.max_speed
        self.min_speed = desc.min_speed
        self.max_length = desc.max_length
        self.min_length = desc.min_length
        
    def update(self, p_x, p_y, heading, l, speed) -> None:
        self.p = np.array([p_x, p_y])
        self.v = np.array([np.cos(heading), np.sin(heading)]) * speed
        self.speed = speed    
        self.heading = heading
        self.l = l
        self.r = l * 6.0
        
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
        return self.desc.is_OS()
    
 