from typing import Dict, List, Tuple

import numpy as np
from utils.asv_utils import EPSILON, N_MILE_TO_M_CONVERSION, o2VisibilityByo1
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.values import Values
from logical_level.models.actor_variable import ActorVariable


class GeometricProperties():
    def __init__(self, var1 : ActorVariable, var2 : ActorVariable, assignments : Assignments):
        self.val1 : Values = assignments[var1]
        self.val2 : Values = assignments[var2]
        self.safety_dist = max(self.val1.r, self.val2.r)
        self.p12 = self.val2.p - self.val1.p
        self.p21 = self.val1.p - self.val2.p
        self.v12 = self.val1.v - self.val2.v
        
        # Define the norm of the relative position (distance(p1 p2))
        self.o_distance = float(max(np.linalg.norm(self.p12), EPSILON))
        
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
        self.dcpa = float(np.linalg.norm(self.p21 + self.v12 * max(0, self.tcpa)))
        
    def get_collision_points(self, time_limit=np.inf) -> List[np.ndarray]:
        # Relative position and velocity
        v_21 = self.val2.v - self.val1.v

        # Coefficients for the quadratic equation
        a = np.dot(v_21, v_21)
        b = 2 * np.dot(self.p12, v_21)
        c = np.dot(self.p12, self.p12) - self.safety_dist**2

        # Calculate discriminant
        discriminant = b**2 - 4*a*c

        collision_points = []

        # Check for real solutions (collision possible)
        if discriminant >= 0:
            sqrt_discriminant = np.sqrt(discriminant)

            # Find times of collision
            t1 = (-b + sqrt_discriminant) / (2 * a)
            t2 = (-b - sqrt_discriminant) / (2 * a)

            # Check if times are within the time limit and positive
            for t in [t1, t2]:
                if 0 <= t <= time_limit:
                    # Compute the collision points
                    collision_point_vessel1 = self.val1.p + self.val1.v * t
                    collision_point_vessel2 = self.val2.p + self.val2.v * t
                    collision_points.append(collision_point_vessel1)
                    collision_points.append(collision_point_vessel2)
        
        # Return the list of collision points as standard list of np.ndarray
        return collision_points


class EvaluationCache(Dict[Tuple[ActorVariable, ActorVariable], GeometricProperties]):
    def __init__(self, assignments : Assignments, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignments = assignments    
    
    def get_props(self, var1 : ActorVariable, var2 : ActorVariable) -> GeometricProperties:
        props = self.get((var1, var2), None)
        if props is None:
            props = GeometricProperties(var1, var2, self.assignments)
            self[(var1, var2)] = props
        return props
    
    def get_collision_points(self, var1 : ActorVariable, var2 : ActorVariable, time_limit=np.inf) -> List[np.ndarray]:
        return self.get_props(var1, var2).get_collision_points(time_limit)
