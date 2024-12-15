from typing import Dict, Tuple

import numpy as np
from asv_utils import EPSILON, N_MILE_TO_M_CONVERSION, o2VisibilityByo1
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.values import Values
from logical_level.models.actor_variable import ActorVariable


class GeometricProperties():
    def __init__(self, var1 : ActorVariable, var2 : ActorVariable, assignments : Assignments):
        self.val1 : Values = assignments(var1)
        self.val2 : Values = assignments(var2)
        self.safety_dist = max(self.val1.r, self.val2.r)
        self.p12 = self.val2.p - self.val1.p
        self.p21 = self.val1.p - self.val2.p
        self.v12 = self.val1.v - self.val2.v
        
        # Define the norm of the relative position (distance(p1 p2))
        self.o_distance = max(np.linalg.norm(self.p12), EPSILON)   
        
        self.cos_p21_v2_theta = np.clip(np.dot(self.p21, self.val2.v) / self.o_distance / self.val2.sp, -1, 1)
        self.angle_p21_v2 = np.arccos(self.cos_p21_v2_theta)        
        self.cos_p12_v1_theta = np.clip(np.dot(self.p12, self.val1.v) / self.o_distance / self.val1.sp, -1, 1)
        self.angle_p12_v1 = np.arccos(self.cos_p12_v1_theta)
        
        self.vis_distance = min(o2VisibilityByo1(self.angle_p12_v1, self.val1.l),
                           o2VisibilityByo1(self.angle_p21_v2, self.val2.l)) *  N_MILE_TO_M_CONVERSION
        # angle between the relative velocity and the relative position vector
        
        self.v12_norm_stable = max(np.linalg.norm(self.v12), EPSILON)
        self.dot_p12_v12 = np.dot(self.p12, self.v12)
        #self.cos_p12_v12_theta = np.clip(self.dot_p12_v12 / self.o_distance / self.v12_norm_stable, -1, 1)
        #self.angle_v12_p12 = np.arccos(self.cos_p12_v12_theta)
        
        self.tcpa = self.dot_p12_v12 / self.v12_norm_stable**2
        self.dcpa = np.linalg.norm(self.p21 + self.v12 * max(0, self.tcpa)) 

class EvaluationCache(Dict[Tuple[ActorVariable, ActorVariable], GeometricProperties]):
    def __init__(self, assignments : Assignments, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignments = assignments    
    
    def get_props(self, var1 : ActorVariable, var2 : ActorVariable):
        if (var1, var2) not in self:
            self[(var1, var2)] = GeometricProperties(var1, var2, self.assignments)
        return self.get((var1, var2))
