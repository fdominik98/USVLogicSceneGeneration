from model.usv_config import (DIST_DRIFT, EPSILON, HEAD_ON_ANGLE, CROSSING_ANGLE, MASTHEAD_ANGLE, OVERTAKE_ANGLE,
                              CONSTRAINT_NUMBER, angle_angle_diff, heading, interval_penalty, o2VisibilityByo1, N_MILE_TO_M_CONVERSION, vector_angle_diff)
from model.vessel import Vessel
import numpy as np
from abc import ABC, abstractmethod
import sys


# Approximated minimum spacing for Coldwell's domain for various conditions, ensuring that neither domain is violated.

# Encounter/Safety Condition                                   | Neither Domain is Violated
# --------------------------------------------------------------------------------
# Head-on (starboard to a target)                              | 3.25L2 - 0.5B2
# Crossing ahead of a target on port or starboard              | 6.1L2 - 0.5L2
# Crossing astern of a target from port or starboard           | 3.9L2 - 0.5L2
# Head-on (port to a target),
# Overtaking (port or starboard to a target)                   | 1.75L2 - 0.5B2


class ColregSituation(ABC):
    in_front_angle_bounds = (0.0, HEAD_ON_ANGLE / 2.0)
    behind_angle_bounds = (MASTHEAD_ANGLE / 2.0, np.pi)
    crossing_angle_bounds = (0.0, CROSSING_ANGLE / 2.0)
    
    def __init__(self, name, vessel1 : Vessel, vessel2 : Vessel) -> None:
        self.vessel1 = vessel1
        self.vessel2 = vessel2
        self.name = name
        self.safety_dist = vessel1.l + vessel2.l  
        self.penalties = [0.0] * CONSTRAINT_NUMBER  
        self.update()
        
        
    def update(self):
        self.p12 = self.vessel2.p - self.vessel1.p
        self.p21 = self.vessel1.p - self.vessel2.p
        self.v12 = self.vessel1.v - self.vessel2.v
        
        self.p12_heading = heading(self.p12)
        self.p21_heading = heading(self.p21)
        
        # Define the norm of the relative position (distance(p1 p2))
        self.o_distance = np.linalg.norm(self.p12)   
        
        self.angle_p21_v2 = angle_angle_diff(self.p21_heading, self.vessel2.heading)
        
        self.angle_p12_v1 = angle_angle_diff(self.p12_heading, self.vessel1.heading)
        
        self.vis_distance = min(o2VisibilityByo1(self.angle_p12_v1, self.vessel1.l),
                           o2VisibilityByo1(self.angle_p21_v2, self.vessel2.l)) *  N_MILE_TO_M_CONVERSION
        
        self._colreg_sit_update()
        
        
    @abstractmethod    
    def _colreg_sit_update(self):
        pass
    
    def vo_computes(self):
        # angle between the relative velocity and the relative position vector
        self.angle_v12_p12 = vector_angle_diff(self.v12, self.p12_heading)      
        
        stable_norm_p12 = max(self.o_distance, EPSILON)
        sin_theta = np.clip(self.safety_dist / stable_norm_p12, -1, 1)
        self.angle_half_cone = abs(np.arcsin(sin_theta)) # [0, pi/2]
        
        
    def constraint_dist_penalty(self):
        return interval_penalty(self.o_distance, (self.vis_distance - DIST_DRIFT, self.vis_distance + DIST_DRIFT))         
        
    def v2_in_front_v1_penalty(self, vision_boundary = (0, np.pi /2)):
        return interval_penalty(self.angle_p12_v1, vision_boundary)

    def vo_collision_penalty(self):
        return interval_penalty(self.angle_v12_p12, (0, self.angle_half_cone))
        
    @abstractmethod
    def info(self):
        print('---------------------------------------------')
        print(self.name)
        print(f'visibility distance: {self.vis_distance}, actual distance {self.o_distance}, penalty: {self.penalties[0]}')    
        
class Overtaking(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel):
        super().__init__(f'{vessel1.id} is overtaking {vessel2.id}', vessel1, vessel2)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_dist = self.constraint_dist_penalty()
        self.constraint_VO = self.vo_collision_penalty()
        
        self.constraint_overtaking1 = interval_penalty(self.angle_p21_v2, self.behind_angle_bounds)
        self.constraint_overtaking2 = self.v2_in_front_v1_penalty()
        self.penalties = [self.constraint_dist, self.constraint_VO, self.constraint_overtaking1, self.constraint_overtaking2]
        
    def info(self):
        super().info()
        print(f'angular distance from overtaking angle v1 behind v2: {np.degrees(self.constraint_overtaking1)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from overtaking angle v2 in front of v1: {np.degrees(self.constraint_overtaking2)} degrees, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
    
        
class HeadOn(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel):
        super().__init__(f'{vessel1.id} and {vessel2.id} are head on', vessel1, vessel2)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_dist = self.constraint_dist_penalty()
        self.constraint_VO = self.vo_collision_penalty()
        
        self.constraint_head_on1 = interval_penalty(self.angle_p21_v2, self.in_front_angle_bounds)
        self.constraint_head_on2 = self.v2_in_front_v1_penalty(vision_boundary=self.in_front_angle_bounds)
        self.penalties = [self.constraint_dist, self.constraint_VO, self.constraint_head_on1, self.constraint_head_on2]
        
    def info(self):
        super().info()
        print(f'angular distance from head on angle v1 in front v2: {np.degrees(self.constraint_head_on1)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from head on angle v2 in front v1: {np.degrees(self.constraint_head_on2)} degrees, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
        
        
class CrossingFromPort(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel):
        super().__init__(f'{vessel1.id} is crossing {vessel2.id} from port', vessel1, vessel2)
        
    def _colreg_sit_update(self):
        self.rotation_angle = HEAD_ON_ANGLE / 2 + CROSSING_ANGLE / 2
        self.vo_computes()
        self.constraint_dist = self.constraint_dist_penalty()
        self.constraint_VO = self.vo_collision_penalty()
        
        rotation_matrix = np.array([
            [np.cos(self.rotation_angle), -np.sin(self.rotation_angle)],
            [np.sin(self.rotation_angle), np.cos(self.rotation_angle)]
        ])
        # Rotate vector
        v2_rot = np.dot(rotation_matrix, self.vessel2.v)
        angle_p21_v2_rot = vector_angle_diff(v2_rot, self.p21_heading)
          
        self.constraint_from_port1 = interval_penalty(angle_p21_v2_rot, self.crossing_angle_bounds)
        self.constraint_from_port2 = self.v2_in_front_v1_penalty()
        self.penalties = [self.constraint_dist, self.constraint_VO, self.constraint_from_port1, self.constraint_from_port2]
        
    def info(self):
        super().info()
        print(f'angular distance from crossing from port angle v1 left ofv2: {np.degrees(self.constraint_from_port1)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from crossing from port angle v2 in front of v1: {np.degrees(self.constraint_from_port2)} degrees, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
        

class NoColreg(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel):
        super().__init__(f'{vessel1.id} is not colliding with {vessel2.id}', vessel1, vessel2)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_None_VO = interval_penalty(self.angle_v12_p12, (self.angle_half_cone, np.pi))
        self.constraint_dist = interval_penalty(self.o_distance, (self.vis_distance, sys.float_info.max))
        
        if self.constraint_None_VO == 0.0:
            self.constraint_dist = interval_penalty(self.o_distance, (self.safety_dist, sys.float_info.max))
        elif self.constraint_dist == 0.0:
            self.constraint_None_VO = 0.0
                
        self.penalties = [self.constraint_dist, self.constraint_None_VO, 0, 0]
        
    def info(self):
        super().info()
        print(f'angular distance from VO cone: {np.degrees(self.constraint_None_VO)} degrees, NO colliding penalty: {self.penalties[1]}')
