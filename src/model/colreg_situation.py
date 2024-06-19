from model.usv_config import *
from model.vessel import Vessel
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional

class ColregSituation(ABC):
    def __init__(self, name, vessel1 : Vessel, vessel2 : Vessel, distance : tuple[float, float]) -> None:
        self.vessel1 = vessel1
        self.vessel2 = vessel2
        self.name = name
        self.r = vessel1.r + vessel2.r  
        
        if distance is None:
            self.distance = [self.r, max_distance]  
        else:
            if distance[0] < 0 or distance[1] > max_distance:
                raise Exception('Distance out of range')
            self.distance = [max(self.r, distance[0]), distance[1]]    
        self.update()
        
    def angle(self, dot_product, norm_a, norm_b):
        norm_a = max(norm_a, epsilon)
        norm_b = max(norm_b, epsilon)
        cos_theta = dot_product / (norm_a * norm_b)
        cos_theta = np.clip(cos_theta, -1, 1)
        angle = np.arccos(cos_theta)
        
        return angle
        
    def update(self):
        self.p12 = self.vessel2.p - self.vessel1.p
        self.p21 = self.vessel1.p - self.vessel2.p
        self.v12 = self.vessel1.v - self.vessel2.v
        
        self.perp_p12 = np.array([-self.p12[1], self.p12[0]])
        
        # Define the norm of the relative position (distance(p1 p2))
        self.norm_p12 = np.linalg.norm(self.p12)

        # Define norm of v12
        self.norm_v12 = np.linalg.norm(self.v12)
        
        self.dot_product_p12_v1  = np.dot(self.p12, self.vessel1.v)  
        self.angle_p12_v1 = self.angle(self.dot_product_p12_v1, self.norm_p12, self.vessel1.speed)    
        
        # Visibility constraint penalty
        self.constraint_vis = interval_penalty(self.norm_p12, self.distance)
        
        self.penalties = [self.constraint_vis]
        
        self._colreg_sit_update()
        self.penalties = penalties_norm(self.penalties, self.distance)
        
    @abstractmethod    
    def _colreg_sit_update(self):
        pass
    
    def vo_computes(self):
        # Define the dot product of the relative velocity and the relative position
        dot_product_v12_p12 = np.dot(self.v12, self.p12)
        # angle between the relative velocity and the relative position vector
        self.angle_v12_p12 = self.angle(dot_product_v12_p12, self.norm_v12, self.norm_p12)
        
        stable_norm_p12 = max(self.norm_p12, epsilon)
        sin_theta = np.clip(self.r / stable_norm_p12, -1, 1)
        self.angle_half_cone = abs(np.arcsin(sin_theta)) # [0, pi/2]
        # Define VO constraint penalty
        self.constraint_VO = 0 if self.angle_v12_p12 < self.angle_half_cone else abs(self.angle_v12_p12 - self.angle_half_cone)
        
    @abstractmethod
    def info(self):
        print('---------------------------------------------')
        print(self.name)
        if self.distance is not None:
            print(f'visibility distance from {self.distance}: {self.constraint_vis}, penalty: {self.penalties[0]}')    
      
        
class Overtake(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : float):
        super().__init__(f'{vessel1.id} is overtaking {vessel2.id}', vessel1, vessel2, distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        # Define p1 overtaking constraint
        self.dot_product_p12_v2  = np.dot(self.p12, self.vessel2.v)
        self.angle_p12_v2 = self.angle(self.dot_product_p12_v2, self.norm_p12, self.vessel2.speed)
        
        self.constraint_overtaking_v1 = 0 if self.angle_p12_v1 < overtake_angle / 2 else (self.angle_p12_v1 - overtake_angle / 2)
        self.constraint_overtaking_v2 = abs(self.angle_p12_v2)
        self.penalties += [self.constraint_VO, self.constraint_overtaking_v1, self.constraint_overtaking_v2]
        
    def info(self):
        super().info()
        print(f'angular distance from overtaking angle for v1: {np.degrees(self.constraint_overtaking_v1)} degs, penalty: {self.penalties[2]}')
        print(f'angular distance from overtaking angle for v2 (from 0): {np.degrees(self.constraint_overtaking_v2)} degs, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degs, penalty: {self.penalties[1]}')
        
        
class HeadOn(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : float):
        super().__init__(f'{vessel1.id} and {vessel2.id} are head on', vessel1, vessel2, distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        # Define head-on constraint penalties
        self.dot_product_p21_v2  = np.dot(self.p21, self.vessel2.v)
        self.angle_p21_v2 = self.angle(self.dot_product_p21_v2, self.norm_p12, self.vessel2.speed)
        
        self.constraint_head_on_v1 = 0 if self.angle_p12_v1 < head_on_angle / 2 else (self.angle_p12_v1 - head_on_angle / 2)
        self.constraint_head_on_v2 = 0 if self.angle_p21_v2 < head_on_angle / 2 else (self.angle_p21_v2 - head_on_angle / 2)
        self.penalties += [self.constraint_VO, self.constraint_head_on_v1, self.constraint_head_on_v2]
        
    def info(self):
        super().info()
        print(f'angular distance from head on angle for v1: {np.degrees(self.constraint_head_on_v1)} degs, penalty: {self.penalties[2]}')
        print(f'angular distance from head on angle for v2: {np.degrees(self.constraint_head_on_v2)} degs, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degs, penalty: {self.penalties[1]}')
        
        
class CrossingFromPort(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : float):
        super().__init__(f'{vessel1.id} is crossing {vessel2.id} from port', vessel1, vessel2, distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        # Define p1 crossing from port constraints
        self.dot_product_perp_p12_v2  = np.dot(self.perp_p12, self.vessel2.v)    
        self.angle_perp_p12_v2 = self.angle(self.dot_product_perp_p12_v2, self.norm_p12, self.vessel2.speed)
        
        self.constraint_from_port_v1 = 0 if self.angle_p12_v1 < crossing_angle / 2 else (self.angle_p12_v1 - crossing_angle / 2)
        self.constraint_from_port_v2 = abs(self.angle_perp_p12_v2)
        self.penalties += [self.constraint_VO, self.constraint_from_port_v1, self.constraint_from_port_v2]
        
    def info(self):
        super().info()
        print(f'angular distance from crossing from port angle for v1: {np.degrees(self.constraint_from_port_v1)} degs, penalty: {self.penalties[2]}')
        print(f'angular distance from crossing from port angle for v2 (from 0): {np.degrees(self.constraint_from_port_v2)} degs, penalty: {self.penalties[3]}')
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degs, penalty: {self.penalties[1]}')
        

class NoColision(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : float):
        super().__init__(f'{vessel1.id} is not colliding with {vessel2.id}', vessel1, vessel2, distance)
        
    def _colreg_sit_update(self):
        self.vo_computes()
        self.constraint_None_VO = 0 if self.angle_v12_p12 > self.angle_half_cone else abs(self.angle_v12_p12 - self.angle_half_cone)
        self.penalties += [self.constraint_None_VO, 0, 0]
        
    def info(self):
        super().info()
        print(f'angular distance from VO cone: {np.degrees(self.constraint_VO)} degs, NO coliding penalty: {self.penalties[1]}')
        
        
class NoConstraint(ColregSituation):
    def __init__(self, vessel1 : Vessel, vessel2 : Vessel, distance : float):
        super().__init__(f'{vessel1.id} and {vessel2.id} has no constraints regarding colision', vessel1, vessel2, distance)
        
    def _colreg_sit_update(self):
        self.penalties += [0, 0, 0]
        
    def info(self):
        super().info()