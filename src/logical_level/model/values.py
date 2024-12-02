from dataclasses import dataclass, field

import numpy as np        

@dataclass(frozen=True)
class Values():
    x : float
    y : float
    h : float
    l : float
    sp: float
    
    p: np.ndarray = field(init=False)
    v: np.ndarray = field(init=False)
    v_norm: np.ndarray = field(init=False)
    v_norm_perp: np.ndarray = field(init=False)
    r: float = field(init=False)
    
    def __post_init__(self):
        object.__setattr__(self, 'p', np.array([self.x, self.y]))
        object.__setattr__(self, 'v', np.array([np.cos(self.h), np.sin(self.h)]) * self.sp)
        object.__setattr__(self, 'v_norm', self.v / self.sp)
        object.__setattr__(self, 'v_norm_perp', np.array([self.v_norm[1], -self.v_norm[0]]))
        object.__setattr__(self, 'r', 4.0 * self.l)
    
   
    

 