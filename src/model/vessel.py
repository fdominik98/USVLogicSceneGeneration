from abc import ABC
import copy
import numpy as np
from model.environment.usv_config import EPSILON, KNOT_TO_MS_CONVERSION


class VesselDesc(ABC):
    def __init__(self, id : int):
        super().__init__()
        self.id = id
        
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselDesc) and
            self.id == value.id)
        
    def __repr__(self) -> str:
        return 'desc'
    
    def __hash__(self):
        return hash((self.id, 'vessel description'))
    
    def is_os(self):
        return isinstance(self, OS)
    

class OS(VesselDesc):
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
        self.name = 'OS' if self.is_OS() else f'TS_{self.id}'
        
    def update(self, p_x, p_y, heading, l, speed):
        self.p = np.array([p_x, p_y])
        self.v = np.array([np.cos(heading), np.sin(heading)]) * speed
        self.speed = speed    
        self.heading = heading
        self.l = l
        self.r = l * 4.0
        return self
    
    def copy_update(self, p_x=None, p_y=None, heading=None, l=None, speed=None):
        return Vessel(self.desc).update(
            p_x or self.p[0],
            p_y or self.p[1],
            heading or self.heading,
            l or self.l,
            speed or self.speed
        )
        
    def do_collide(self, other):
        return np.linalg.norm(self.p - other.p) < max(self.r, other.r)
        
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
        return self.desc.is_os()
    
    def p_3d(self):
        return [self.p[0], self.p[1], 5]
    
    def v_3d(self):
        return [self.v[0], self.v[1], 5]
    
 