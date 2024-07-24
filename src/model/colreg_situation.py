from model.usv_config import epsilon, head_on_angle, crossing_angle, overtake_angle
from model.vessel import Vessel
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional

class ColregSituation(ABC):
    def __init__(self, name, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float) -> None:
        self.vessel1 = vessel1
        self.vessel2 = vessel2
        self.name = name
        self.r = vessel1.r + vessel2.r  
        
        if distance is None:
            self.distance = (self.r, max_distance)  
        else:
            if distance[0] < 0 or distance[1] > max_distance:
                raise Exception('Distance out of range')
            self.distance = (max(self.r, distance[0]), distance[1])    
        self.update()
        
    def angle(self, dot_product, norm_a, norm_b):
        norm_a = max(norm_a, epsilon)
        norm_b = max(norm_b, epsilon)
        cos_theta = dot_product / (norm_a * norm_b)
        cos_theta = np.clip(cos_theta, -1, 1)
        return np.arccos(cos_theta)
    
    def interval_penalty(self, value, boundaries):
        minimum, maximum = boundaries
        if value < minimum:
            return minimum - value
        elif value > maximum:
            return value - maximum
        else:
            return 0.0 
        
    def update(self):
        self.p12 = self.vessel2.p - self.vessel1.p
        self.p21 = self.vessel1.p - self.vessel2.p
        self.v12 = self.vessel1.v - self.vessel2.v
        
        # Define the norm of the relative position (distance(p1 p2))
        self.norm_p12 = np.linalg.norm(self.p12)      
        
        # Visibility constraint penalty
        self.constraint_vis = self.interval_penalty(self.norm_p12, self.distance)        
        self.penalties = [self.constraint_vis]
        
        self._colreg_sit_update()
        # self.penalties = penalties_norm(self.penalties, self.distance)
        
    @abstractmethod    
    def _colreg_sit_update(self):
        pass
    
    def vo_computes(self):
        # Define norm of v12
        self.norm_v12 = np.linalg.norm(self.v12)
        # Define the dot product of the relative velocity and the relative position
        dot_product_v12_p12 = np.dot(self.v12, self.p12)
        # angle between the relative velocity and the relative position vector
        self.angle_v12_p12 = self.angle(dot_product_v12_p12, self.norm_v12, self.norm_p12)
        
        stable_norm_p12 = max(self.norm_p12, epsilon)
        sin_theta = np.clip(self.r / stable_norm_p12, -1, 1)
        self.angle_half_cone = abs(np.arcsin(sin_theta)) # [0, pi/2]
        # Define VO constraint penalty
        self.constraint_VO = self.interval_penalty(self.angle_v12_p12, (0, self.angle_half_cone))
        
    @abstractmethod
    def info(self):
        print('---------------------------------------------')
        print(self.name)
        if self.distance is not None:
            print(f'visibility distance from {self.distance}: {self.constraint_vis}, penalty: {self.penalties[0]}')    
      
        
class Overtake(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float):
        self.angle_bounds = (0.0, overtake_angle / 2.0)
        super().__init__(f'{vessel1.id} is overtaking {vessel2.id}', vessel1, vessel2, distance, max_distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_overtaking = self.angle_distance()
        self.penalties += [self.constraint_VO, self.constraint_overtaking]
        
    def info(self):
        super().info()
        print(f'angular distance from overtaking angle: {np.degrees(self.constraint_overtaking)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
        
    def angle_distance(self):                
        dot_product_p12_v2  = np.dot(self.p12, self.vessel2.v)
        angle_p12_v2 = abs(self.angle(dot_product_p12_v2, self.norm_p12, self.vessel2.speed))
        return self.interval_penalty(angle_p12_v2, self.angle_bounds)
        
        
class HeadOn(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float):
        self.angle_bounds = (0.0, head_on_angle / 2.0)
        super().__init__(f'{vessel1.id} and {vessel2.id} are head on', vessel1, vessel2, distance, max_distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_head_on = self.angle_distance()
        self.penalties += [self.constraint_VO, self.constraint_head_on]
        
    def info(self):
        super().info()
        print(f'angular distance from head on angle: {np.degrees(self.constraint_head_on)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
        
    def angle_distance(self):
        dot_product_p21_v2 = np.dot(self.p21, self.vessel2.v)
        angle_p21_v2 = self.angle(dot_product_p21_v2, self.norm_p12, self.vessel2.speed)        
        return self.interval_penalty(angle_p21_v2, self.angle_bounds)
        
class CrossingFromPort(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float):
        self.angle_bounds = (0.0, crossing_angle / 2.0)
        self.rotation_angle = head_on_angle / 2 + crossing_angle / 2
        super().__init__(f'{vessel1.id} is crossing {vessel2.id} from port', vessel1, vessel2, distance, max_distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_from_port = self.angle_distance()
        self.penalties += [self.constraint_VO, self.constraint_from_port]
        
    def angle_distance(self):
        # Rotation matrix
        rotation_matrix = np.array([
            [np.cos(self.rotation_angle), -np.sin(self.rotation_angle)],
            [np.sin(self.rotation_angle), np.cos(self.rotation_angle)]
        ])
        # Rotate vector
        v2_rot = np.dot(rotation_matrix, self.vessel2.v)
        dot_product_p21_v2_rot = np.dot(self.p21, v2_rot)
        angle_p21_v2_rot = self.angle(dot_product_p21_v2_rot, self.norm_p12, self.vessel2.speed)     
        return self.interval_penalty(angle_p21_v2_rot, self.angle_bounds)
        
    def info(self):
        super().info()
        print(f'angular distance from crossing from port angle: {np.degrees(self.constraint_from_port)} degrees, penalty: {self.penalties[2]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, penalty: {self.penalties[1]}')
        

class NoColreg(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : Optional[tuple[float, float]], max_distance : float):
        super().__init__(f'{vessel1.id} is not colliding with {vessel2.id}', vessel1, vessel2, distance, max_distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_None_VO = self.interval_penalty(self.angle_v12_p12, (self.angle_half_cone, np.pi))
        
        if self.constraint_None_VO == 0.0 or self.constraint_vis == 0.0:
            self.constraint_None_VO = 0.0
            self.constraint_vis = 0.0
                
        self.penalties += [self.constraint_None_VO, 0]
        
    def info(self):
        super().info()
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degrees, NO colliding penalty: {self.penalties[1]}')
