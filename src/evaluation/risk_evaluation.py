import copy
from typing import List, Tuple
import numpy as np
from model.environment.usv_config import N_MILE_TO_M_CONVERSION
from model.environment.usv_environment import USVEnvironment
from model.relation import Relation
from model.relation_types import MayCollide
from model.vessel import Vessel


class RiskVector():
    def __init__(self, env : USVEnvironment) -> None:
        self.proximity_vectors = [ProximityRiskIndex(rel) for rel in env.relations if rel.has_os()]
        self.nav_risk_vector = NavigationRiskIndex(env, env.get_vessel_by_id(0))
            
        self.max_proximity_index = max(self.proximity_vectors, key=lambda obj: obj.proximity_index)
        #self.safe_navigation_area_index = self.nav_risk_vector.find_safe_navigation_area_index()
        self.danger_sector = self.nav_risk_vector.find_danger_sector()
        
        self.risk_vector = np.array([self.max_proximity_index.dcpa,
                                     self.max_proximity_index.tcpa,
                                     self.danger_sector,
                                     self.max_proximity_index.proximity_index])
        
        #self.distance = (pow(np.e, np.linalg.norm(self.risk_vector) / np.sqrt(3)) - 1) / (np.e - 1)
        

class ProximityRiskIndex():
    def __init__(self, relation : Relation) -> None:
        self.dist = relation.o_distance
        self.tcpa = relation.tcpa
        self.dcpa = relation.dcpa
        
        dr = 1 * N_MILE_TO_M_CONVERSION
        ts = 10 * 60
        
        if self.tcpa < 0 or self.tcpa > ts:
            self.dcpa_norm = 0
            self.tcpa_norm = 0
        else:       
            if self.dcpa < relation.safety_dist:
                self.dcpa_norm = 1
            else:
                #self.dcpa_norm = (pow(np.e, (dr - self.dcpa) / (dr - relation.safety_dist)) - 1) / (np.e - 1)
                self.dcpa_norm = (pow(np.e, (dr - self.dcpa) / (dr - relation.safety_dist)) - 1) / (np.e - 1)
            #self.tcpa_norm = (pow(np.e, (ts - self.tcpa) / ts) - 1) / (np.e - 1)
            self.tcpa_norm = (pow(np.e, (ts - self.tcpa) / ts) - 1) / (np.e - 1)
        if self.dcpa_norm * self.tcpa_norm > 0:
            self.proximity_index = np.sqrt(self.dcpa_norm * self.tcpa_norm)
        else:
            self.proximity_index = 0
        
class NavigationRiskIndex():
    def __init__(self, env : USVEnvironment, vessel : Vessel) -> None:
        self.env = env
        self.vessel = vessel
    
    def will_collide(self, heading, speed) -> bool:
        new_vessel = copy.deepcopy(self.vessel)
        new_vessel.update(self.vessel.p[0], self.vessel.p[1], heading, self.vessel.l, speed)
        for vessel2 in self.env.vessels:
            if vessel2.id == new_vessel.id:
                continue
            rel = Relation(new_vessel, [MayCollide()], vessel2)
            pr_i = ProximityRiskIndex(rel)
            if pr_i.dcpa < rel.safety_dist:
                return True
        return False
    
    def find_danger_sector(self) -> float:
        for i in range(91):
            if not self.will_collide(self.vessel.heading + np.radians(i), self.vessel.speed):
                break
        for j in range(91):
            if not self.will_collide(self.vessel.heading - np.radians(j), self.vessel.speed):
                break
        return pow((i + j) / 180, 0.33)
            
    def find_safe_navigation_area_index(self) -> float:
        collides = 0
        no_collides = 0
        partitions = 50
        speeds = [i * (self.vessel.max_speed / partitions)  for i in range(1, partitions + 1)]  
        for speed in speeds:
            for i in range(0, 180):
                for direction in [-1, 1]:  # -1 for counterclockwise, 1 for clockwise
                    if self.will_collide(self.vessel.heading + direction * np.radians(i), speed):
                        collides += 1
                    else:
                        no_collides += 1
        return (pow(np.e, collides / (collides + no_collides)) - 1) / (np.e - 1)
    