import copy
from typing import List
import numpy as np
from model.environment.usv_config import N_MILE_TO_M_CONVERSION
from model.environment.usv_environment import USVEnvironment
from model.relation import Relation
from model.relation_types import MayCollide
from model.vessel import Vessel


class RiskVector():
    def __init__(self, env : USVEnvironment) -> None:
        self.proximity_vectors : List[ProximityRiskVector] = []
        
        for rel in env.relations:
            if not rel.has_os():
                continue
            self.proximity_vectors.append(ProximityRiskVector(rel))
            
        self.nav_risk_vector = NavigationRiskVector(env, env.get_vessel_by_id(0))
            
        self.max_proximity = max(self.proximity_vectors, key=lambda obj: obj.encounter_dist)
        self.risk_vector = np.array([self.max_proximity.encounter_dist,
                                     self.nav_risk_vector.find_safe_navigation_ratio(), 
                                     self.nav_risk_vector.find_minimum_turning_metric()])
        self.distance = (pow(np.e, np.linalg.norm(self.risk_vector) / np.sqrt(3)) - 1) / (np.e - 1)
        

class ProximityRiskVector():
    def __init__(self, relation : Relation) -> None:
        self.dist = relation.o_distance
        self.tcpa = relation.dot_p12_v12 / relation.v12_norm_stable**2
        self.dcpa = np.linalg.norm(relation.p21 + relation.v12 * max(0, self.tcpa)) 
        
        dr = 3 * N_MILE_TO_M_CONVERSION
        ts = 1800
        
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
        self.encounter_dist = np.sqrt(self.dcpa_norm * self.tcpa_norm)
        
class NavigationRiskVector():
    def __init__(self, env : USVEnvironment, vessel : Vessel) -> None:
        self.env = env
        self.vessel = vessel
    
    def will_collide(self, heading, speed) -> bool:
        new_vessel = copy.deepcopy(self.vessel)
        new_vessel.update(self.vessel.p[0], self.vessel.p[1], heading, self.vessel.l, speed)
        for vessel2 in self.env.vessels:
            if vessel2.id == new_vessel:
                continue
            rel = Relation(new_vessel, [MayCollide(True)], vessel2)
            if rel.collision_relations[0].get_penalty_norm() > 0.0:
                return True
        return False
    
    def find_minimum_turning_metric(self) -> float:
        for i in range(0, 180):
            if not (self.will_collide(self.vessel.heading + np.radians(i), self.vessel.speed) and
                    self.will_collide(self.vessel.heading - np.radians(i), self.vessel.speed)):
                return (pow(np.e, i / 180 / 0.25) - 1) / (np.e - 1)
        return 0.0
            
    def find_safe_navigation_ratio(self) -> float:
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
    