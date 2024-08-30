from model.usv_config import (DIST_DRIFT, EPSILON, BOW_ANGLE, BEAM_ANGLE, MASTHEAD_LIGHT_ANGLE, MAX_DISTANCE, STERN_ANGLE,
                              angle_angle_diff, heading, interval_distance, o2VisibilityByo1, N_MILE_TO_M_CONVERSION, strict_distance, vector_angle_diff)
from model.vessel import Vessel
import numpy as np
from abc import ABC, abstractmethod

class ColregSituation(ABC):
    def __init__(self, name, vessel1 : Vessel, vessel2 : Vessel) -> None:
        self.vessel1 = vessel1
        self.vessel2 = vessel2
        self.name = name
        self.safety_dist = vessel1.r + vessel2.r  
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
        
        self.vis_distance = min(o2VisibilityByo1(self.angle_p12_v1, self.vessel1.r),
                           o2VisibilityByo1(self.angle_p21_v2, self.vessel2.r)) *  N_MILE_TO_M_CONVERSION
        self.vo_computes()
        
    @abstractmethod
    def penalties(self) -> list[tuple[float, float]]:
        pass
        
    @abstractmethod
    def strict_penalties(self) -> list[tuple[float, float]]:
        pass
    
    def vo_computes(self):
        # angle between the relative velocity and the relative position vector
        self.angle_v12_p12 = vector_angle_diff(self.v12, self.p12_heading)      
        
        stable_norm_p12 = max(self.o_distance, EPSILON)
        sin_theta = np.clip(self.safety_dist / stable_norm_p12, -1, 1)
        self.angle_half_cone = abs(np.arcsin(sin_theta)) # [0, pi/2]
        
        
    def visibility_dist(self) -> tuple[float, float]:
        return interval_distance(self.o_distance, (self.vis_distance - DIST_DRIFT, self.vis_distance + DIST_DRIFT), is_angle=False) 
    
    def strict_visibility_dist(self) -> tuple[float, float]:
        return strict_distance(self.o_distance, self.vis_distance, is_angle=False)        
        
    def v2_in_front_v1_dist(self, vision_boundary) -> tuple[float, float]:
        return interval_distance(self.angle_p12_v1, vision_boundary)
    
    def strict_v2_in_front_v1_dist(self, goal_angle) -> tuple[float, float]:
        return strict_distance(self.angle_p12_v1, goal_angle)

    def vo_collision_dist(self) -> tuple[float, float]:
        return interval_distance(self.angle_v12_p12, (0, self.angle_half_cone))
    
    def strict_vo_collision_dist(self) -> tuple[float, float]:
        return strict_distance(self.angle_v12_p12, 0)
        
    def info(self):
        penalties = self.penalties()
        strict_penalties = self.strict_penalties()
        print('---------------------------------------------')
        print(self.name)
        print(f'Visibility dist: {self.vis_distance}, actual dist: {self.o_distance}, penalty: {penalties[0][0]}, penalty norm: {penalties[0][1]}, strict penalty: {strict_penalties[0][0]}, strict penalty norm: {strict_penalties[0][1]}')    
        print(f'Angular penalty from VO cone: {np.degrees(penalties[1][0])} degs, penalty norm: {penalties[1][1]}, strict penalty: {np.degrees(strict_penalties[1][0])}, strict penalty norm: {strict_penalties[1][1]}')
        self.do_info(penalties, strict_penalties)
        
    @abstractmethod
    def do_info(self, penalties : list[tuple, tuple], strict_penalties : list[tuple, tuple]):
        pass
    
class Overtaking(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel):
        super().__init__(f'{vessel1.name} is overtaking {vessel2.name}', vessel1, vessel2)
        
    def penalties(self) -> list[tuple[float, float]]:
        return [
            self.visibility_dist(),
            self.vo_collision_dist(),
            interval_distance(self.angle_p21_v2, (MASTHEAD_LIGHT_ANGLE / 2.0, np.pi)),
            self.v2_in_front_v1_dist((0, MASTHEAD_LIGHT_ANGLE /2))
        ]
        
    def strict_penalties(self) -> list[tuple[float, float]]:
        return [
            self.strict_visibility_dist(),
            self.strict_vo_collision_dist(),
            strict_distance(self.angle_p21_v2, np.pi),
            self.strict_v2_in_front_v1_dist(0)
        ]
        
  
    def do_info(self, penalties : list[tuple, tuple], strict_penalties : list[tuple, tuple]):
        print(f'Angular penalty of v1 behind v2: {np.degrees(penalties[2][0])} degs, penalty norm: {penalties[2][1]}, strict penalty: {np.degrees(strict_penalties[2][0])}, strict penalty norm: {strict_penalties[2][1]}')
        print(f'Angular penalty of v2 in front of v1: {np.degrees(penalties[3][0])} degs, penalty norm: {penalties[3][1]}, strict penalty: {np.degrees(strict_penalties[3][0])}, strict penalty norm: {strict_penalties[3][1]}')
    
        
class HeadOn(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel):
        super().__init__(f'{vessel1.name} and {vessel2.name} are head on', vessel1, vessel2)
        
    def penalties(self) -> list[tuple[float, float]]:
        return [
            self.visibility_dist(),
            self.vo_collision_dist(),
            interval_distance(self.angle_p21_v2, (0.0, BOW_ANGLE / 2.0)),
            self.v2_in_front_v1_dist((0.0, BOW_ANGLE / 2.0))
        ]
        
    def strict_penalties(self) -> list[tuple[float, float]]:
        return [
            self.strict_visibility_dist(),
            self.strict_vo_collision_dist(),
            strict_distance(self.angle_p21_v2, 0),
            self.strict_v2_in_front_v1_dist(0)
        ]   
        
    def do_info(self, penalties : list[tuple, tuple], strict_penalties : list[tuple, tuple]):
        print(f'Angular penalty of v1 in front v2: {np.degrees(penalties[2][0])} degs, penalty norm: {penalties[2][1]}, strict penalty: {np.degrees(strict_penalties[2][0])}, strict penalty norm: {strict_penalties[2][1]}')
        print(f'Angular penalty of v2 in front of v1: {np.degrees(penalties[3][0])} degs, penalty norm: {penalties[3][1]}, strict penalty: {np.degrees(strict_penalties[3][0])}, strict penalty norm: {strict_penalties[3][1]}')
        
class CrossingFromPort(ColregSituation):
    rotation_angle = (BOW_ANGLE + BEAM_ANGLE) / 2
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel):
        super().__init__(f'{vessel1.name} is crossing {vessel2.name} from port', vessel1, vessel2)
        
    def penalties(self) -> list[tuple[float, float]]:
        angle_p21_v2_rot = vector_angle_diff(self.rotated_v2(), self.p21_heading)
        return [
            self.visibility_dist(),
            self.vo_collision_dist(),
            interval_distance(angle_p21_v2_rot, (0.0, BEAM_ANGLE / 2.0)),
            self.v2_in_front_v1_dist((0, MASTHEAD_LIGHT_ANGLE /2))
        ]
        
    def strict_penalties(self) -> list[tuple[float, float]]:
        angle_p21_v2_rot = vector_angle_diff(self.rotated_v2(), self.p21_heading)
        return [
            self.strict_visibility_dist(),
            self.strict_vo_collision_dist(),
            strict_distance(angle_p21_v2_rot, 0),
            self.strict_v2_in_front_v1_dist(0)
        ]
        
    def rotated_v2(self):
        rotation_matrix = np.array([
            [np.cos(self.rotation_angle), -np.sin(self.rotation_angle)],
            [np.sin(self.rotation_angle), np.cos(self.rotation_angle)]
        ])
        # Rotate vector
        return np.dot(rotation_matrix, self.vessel2.v)
        
    def do_info(self, penalties : list[tuple, tuple], strict_penalties : list[tuple, tuple]):
        print(f'Angular penalty of v1 left of v2: {np.degrees(penalties[2][0])} degs, penalty norm: {penalties[2][1]}, strict penalty: {np.degrees(strict_penalties[2][0])}, strict penalty norm: {strict_penalties[2][1]}')
        print(f'Angular penalty of v2 in front of v1: {np.degrees(penalties[3][0])} degs, penalty norm: {penalties[3][1]}, strict penalty: {np.degrees(strict_penalties[3][0])}, strict penalty norm: {strict_penalties[3][1]}')

class NoColreg(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel):
        super().__init__(f'{vessel1.name} is not colliding with {vessel2.name}', vessel1, vessel2)
        
    def penalties(self) -> list[tuple[float, float]]:
        vo_collision_penalty = interval_distance(self.angle_v12_p12, (self.angle_half_cone, np.pi))
        visibility_dist_penalty = interval_distance(self.o_distance, (self.vis_distance, MAX_DISTANCE), is_angle=False)
        
        if vo_collision_penalty == (0.0, 0.0):
            visibility_dist_penalty = interval_distance(self.o_distance, (self.safety_dist, MAX_DISTANCE), is_angle=False)
        elif visibility_dist_penalty == (0.0, 0.0):
            vo_collision_penalty = (0.0, 0.0)
        return [
            visibility_dist_penalty,
            vo_collision_penalty,
            (0.0, 0.0),
            (0.0, 0.0)
        ]
        
    def strict_penalties(self) -> list[tuple[float, float]]:
        return self.penalties()  

    def do_info(self, penalties : list[tuple, tuple], strict_penalties : list[tuple, tuple]):
        pass
        