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
        self.distance = np.sqrt(sum([x**2 for x in self.risk_vector]))
        

class ProximityRiskVector():
    def __init__(self, relation : Relation) -> None:
        self.dist = relation.o_distance
        self.tcpa = relation.tcpa
        self.dcpa = relation.dcpa
        
        dr = 3 * N_MILE_TO_M_CONVERSION
        ts = 3000
        
        if self.tcpa < 0 or self.tcpa > ts or self.dcpa > dr:
            self.dcpa_norm = 0
            self.tcpa_norm = 0
        else:       
            if self.dcpa < relation.safety_dist:
                self.dcpa_norm = 1
            else:
                #self.dcpa_norm = (pow(np.e, (dr - self.dcpa) / (dr - relation.safety_dist)) - 1) / (np.e - 1)
                self.dcpa_norm = 1 - (self.dcpa / dr)
            #self.tcpa_norm = (pow(np.e, (ts - self.tcpa) / ts) - 1) / (np.e - 1)
            self.tcpa_norm = 1 - (self.tcpa / ts)
        self.encounter_dist = np.sqrt(self.dcpa_norm * self.tcpa_norm)
        
class NavigationRiskVector():
    def __init__(self, env : USVEnvironment, vessel : Vessel) -> None:
        self.env = env
        self.vessel = vessel
    
    def will_collide(self, heading, speed) -> bool:
        new_vessel = copy.deepcopy(self.vessel)
        new_vessel.update(self.vessel.p[0], self.vessel.p[1], heading, speed)
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
                return i / 180 / 0.25
        return 0.0
            
    def find_safe_navigation_ratio(self) -> float:
        collides = 0
        no_collides = 0
        partitions = 30
        speeds = [i * (self.vessel.max_speed / partitions)  for i in range(1, partitions + 1)]  
        for speed in speeds:
            for i in range(0, 180):
                for direction in [-1, 1]:  # -1 for counterclockwise, 1 for clockwise
                    if self.will_collide(self.vessel.heading + direction * np.radians(i), speed):
                        collides += 1
                    else:
                        no_collides += 1
        return collides / (collides + no_collides)