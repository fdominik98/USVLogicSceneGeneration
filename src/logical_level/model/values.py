from dataclasses import dataclass

import numpy as np        

@dataclass(frozen=True)
class Values():
    x : float
    y : float
    h : float
    l : float
    sp: float
    
    def __post_init__(self):
        self.p = np.array([self.x, self.y])
        self.v = np.array([np.cos(self.h), np.sin(self.h)]) * self.sp
        self.v_norm = self.v / self.sp
        self.v_norm_perp = np.array([self.v_norm[1], -self.v_norm[0]])
    
   
    

 