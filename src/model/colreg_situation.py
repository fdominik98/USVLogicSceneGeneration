from model.usv_config import EPSILON, HEAD_ON_ANGLE, CROSSING_ANGLE, OVERTAKE_ANGLE, CONSTRAINT_NUMBER, interval_penalty, angle
from model.vessel import Vessel
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional

class ColregSituation(ABC):
    in_front_angle_bounds = (0.0, HEAD_ON_ANGLE / 2.0)
    behind_angle_bounds = (0.0, OVERTAKE_ANGLE / 2.0)
    crossing_angle_bounds = (0.0, CROSSING_ANGLE / 2.0)
    
    def __init__(self, name, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float) -> None:
        self.vessel1 = vessel1
        self.vessel2 = vessel2
        self.name = name
        self.r = vessel1.r + vessel2.r  
        self.penalties = [0.0] * CONSTRAINT_NUMBER
        
        if distance is None:
            self.distance = (self.r, max_distance)  
        else:
            if distance[0] < 0 or distance[1] > max_distance:
                raise Exception('Distance out of range')
            self.distance = (max(self.r, distance[0]), distance[1]) 
        self.min_distance = (self.r, self.distance[1])   
        self.update()
        
 
        
    def update(self):
        self.p12 = self.vessel2.p - self.vessel1.p
        self.p21 = self.vessel1.p - self.vessel2.p
        self.v12 = self.vessel1.v - self.vessel2.v
        
        # Define the norm of the relative position (distance(p1 p2))
        self.norm_p12 = np.linalg.norm(self.p12)      
        
        # Visibility constraint penalty
        self.constraint_vis = interval_penalty(self.norm_p12, self.distance)        
        
        self._colreg_sit_update()
        # self.penalties = penalties_norm(self.penalties, self.distance)
        
    def v2_in_front_v1(self, vision_boundary = (0, np.pi /2)):
        dot_product_p12_v1 = np.dot(self.p12, self.vessel1.v)
        angle_p12_v1 = angle(dot_product_p12_v1, self.norm_p12, self.vessel1.speed)        
        return interval_penalty(angle_p12_v1, vision_boundary)
    

        
    @abstractmethod    
    def _colreg_sit_update(self):
        pass
    
    def vo_computes(self):
        # Define norm of v12
        self.norm_v12 = np.linalg.norm(self.v12)
        # Define the dot product of the relative velocity and the relative position
        dot_product_v12_p12 = np.dot(self.v12, self.p12)
        # angle between the relative velocity and the relative position vector
        self.angle_v12_p12 = angle(dot_product_v12_p12, self.norm_v12, self.norm_p12)
        
        stable_norm_p12 = max(self.norm_p12, EPSILON)
        sin_theta = np.clip(self.r / stable_norm_p12, -1, 1)
        self.angle_half_cone = abs(np.arcsin(sin_theta)) # [0, pi/2]
        # Define VO constraint penalty
        self.constraint_VO = interval_penalty(self.angle_v12_p12, (0, self.angle_half_cone))
        
    @abstractmethod
    def info(self):
        print('---------------------------------------------')
        print(self.name)
        if self.distance is not None:
            print(f'visibility distance from {self.distance}: {self.constraint_vis}, penalty: {self.penalties[0]}')    
      
        
class Overtaking(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float):
        super().__init__(f'{vessel1.id} is overtaking {vessel2.id}', vessel1, vessel2, distance, max_distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_overtaking1 = self.v1_behind_v2()
        self.constraint_overtaking2 = self.v2_in_front_v1()
        self.penalties = [self.constraint_vis, self.constraint_VO, self.constraint_overtaking1, self.constraint_overtaking2]
        
    def info(self):
        super().info()
        print(f'angular distance from overtaking angle v1 behind v2: {np.degrees(self.constraint_overtaking1)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from overtaking angle v2 in front of v1: {np.degrees(self.constraint_overtaking2)} degrees, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
    
    def v1_behind_v2(self):
        dot_product_p12_v2  = np.dot(self.p12, self.vessel2.v)
        angle_p12_v2 = abs(angle(dot_product_p12_v2, self.norm_p12, self.vessel2.speed))
        return interval_penalty(angle_p12_v2, self.behind_angle_bounds)
        
        
class HeadOn(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float):
        super().__init__(f'{vessel1.id} and {vessel2.id} are head on', vessel1, vessel2, distance, max_distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_head_on1 = self.v1_in_front_v2()
        self.constraint_head_on2 = self.v2_in_front_v1(vision_boundary=self.in_front_angle_bounds)
        self.penalties = [self.constraint_vis, self.constraint_VO, self.constraint_head_on1, self.constraint_head_on2]
        
    def info(self):
        super().info()
        print(f'angular distance from head on angle v1 in front v2: {np.degrees(self.constraint_head_on1)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from head on angle v2 in front v1: {np.degrees(self.constraint_head_on2)} degrees, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
        
    def v1_in_front_v2(self):
        dot_product_p21_v2 = np.dot(self.p21, self.vessel2.v)
        angle_p21_v2 = angle(dot_product_p21_v2, self.norm_p12, self.vessel2.speed)        
        return interval_penalty(angle_p21_v2, self.in_front_angle_bounds)
    
    
        
class CrossingFromPort(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float):
        self.rotation_angle = HEAD_ON_ANGLE / 2 + CROSSING_ANGLE / 2
        super().__init__(f'{vessel1.id} is crossing {vessel2.id} from port', vessel1, vessel2, distance, max_distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_from_port1 = self.v1_left_of_v2()
        self.constraint_from_port2 = self.v2_in_front_v1()
        self.penalties = [self.constraint_vis, self.constraint_VO, self.constraint_from_port1, self.constraint_from_port2]
        
    def v1_left_of_v2(self):
        # Rotation matrix
        rotation_matrix = np.array([
            [np.cos(self.rotation_angle), -np.sin(self.rotation_angle)],
            [np.sin(self.rotation_angle), np.cos(self.rotation_angle)]
        ])
        # Rotate vector
        v2_rot = np.dot(rotation_matrix, self.vessel2.v)
        dot_product_p21_v2_rot = np.dot(self.p21, v2_rot)
        angle_p21_v2_rot = angle(dot_product_p21_v2_rot, self.norm_p12, self.vessel2.speed)     
        return interval_penalty(angle_p21_v2_rot, self.crossing_angle_bounds)
        
    def info(self):
        super().info()
        print(f'angular distance from crossing from port angle v1 left ofv2: {np.degrees(self.constraint_from_port1)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from crossing from port angle v2 in front of v1: {np.degrees(self.constraint_from_port2)} degrees, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
        

class NoColreg(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float):
        super().__init__(f'{vessel1.id} is not colliding with {vessel2.id}', vessel1, vessel2, distance, max_distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_None_VO = interval_penalty(self.angle_v12_p12, (self.angle_half_cone, np.pi))
        
        if self.constraint_None_VO == 0.0 or self.constraint_vis == 0.0:
            self.constraint_None_VO = 0.0
            self.constraint_vis = min(self.constraint_vis, interval_penalty(self.norm_p12, self.min_distance))
                
        self.penalties = [self.constraint_vis, self.constraint_None_VO, 0, 0]
        
    def info(self):
        super().info()
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, NO colliding penalty: {self.penalties[1]}')
