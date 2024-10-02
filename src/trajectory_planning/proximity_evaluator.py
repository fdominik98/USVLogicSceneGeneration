from typing import Dict, List, Tuple
import numpy as np
from model.environment.usv_environment import USVEnvironment
from model.vessel import Vessel
import copy
from model.relation import Relation
from model.relation_types import MayCollide
from model.environment.usv_config import N_MILE_TO_M_CONVERSION

class ProximityVector():
    def __init__(self, relation : Relation) -> None:
        theta = np.pi - relation.angle_v12_p12
        self.dist = relation.o_distance
        self.dcpa = self.dist * abs(np.sin(theta))
        self.tcpa = relation.dot_p12_v12 / relation.v12_norm_stable**2
        
        dr = 6 * N_MILE_TO_M_CONVERSION
        ts = 60 * 60 * 60 # 1 hour
        self.dcpa_norm = 0 if self.tcpa < 0 or self.tcpa > ts else (pow(np.e, (dr - self.dcpa) / (dr - relation.safety_dist)) - 1) / (np.e - 1)
        self.tcpa_norm = 0 if self.tcpa < 0 or self.tcpa > ts else (pow(np.e, (ts - self.tcpa) / ts) - 1) / (np.e - 1)

class ProximityMetric():
    def __init__(self, relation : Relation) -> None:
        self.vectors : List[ProximityVector] = []
        self.len = 0
        self.relation = relation
        
    def append(self, pv : ProximityVector):
        self.vectors.append(pv)
        self.len += 1
        
    def get_first_dcpa(self) -> float:
        return self.vectors[0].dcpa
    
    def get_first_distance(self) -> float:
        return self.vectors[0].dist
    
    def get_first_tcpa(self) -> float:
        return self.vectors[0].tcpa

class ProximityEvaluator():
    def __init__(self, env : USVEnvironment, trajectories: Dict[int, List[Tuple[float,float,float,float]]]) -> None:
        self.env = env
        self.trajectories = trajectories
        self.metrics : List[ProximityMetric] = []
        
        for relation in env.relations:
            if relation.vessel1.is_OS() or relation.vessel2.is_OS():
                self.metrics.append(self.calculate_pair(relation))
        
    def calculate_pair(self, relation : Relation) -> ProximityMetric:
        dyn_rel = copy.deepcopy(relation)
        v1 = dyn_rel.vessel1
        v2 = dyn_rel.vessel2
        
        traj1 = self.trajectories[v1.id]
        traj2 = self.trajectories[v2.id]
        
        metrics = ProximityMetric(relation)
        for s, (pos1, pos2) in enumerate(zip(traj1, traj2)):
            v1.update(*pos1)
            v2.update(*pos2)
            dyn_rel.update()
            metrics.append(ProximityVector(relation))
            
        return metrics
    
class RiskEvaluator():
    def __init__(self, env : USVEnvironment, trajectories: Dict[int, List[Tuple[float,float,float,float]]]) -> None:
        self.env = env
        self.trajectories = trajectories
        self.risk_metrics : Dict[int, List[float]] = {v.id : [] for v in env.vessels}
        
        dyn_env = copy.deepcopy(env)
        
        for t in range(len(trajectories[0])):
            if t % 30 == 0:
                for o in dyn_env.vessels:
                    traj = trajectories[o.id]
                    o.update(*(traj[t]))
                for vessel1 in dyn_env.vessels:
                    # if not vessel1.is_OS():
                    #     continue
                    for i in range(0, 180):
                        new_vcclkw = copy.deepcopy(vessel1)
                        new_vcclkw.update(vessel1.p[0], vessel1.p[1], vessel1.heading + np.radians(i), vessel1.speed)
                        new_vclkw = copy.deepcopy(vessel1)
                        new_vcclkw.update(vessel1.p[0], vessel1.p[1], vessel1.heading - np.radians(i), vessel1.speed)
                        if not (self.will_collide(dyn_env, new_vcclkw) and self.will_collide(dyn_env, new_vclkw)):
                            break
                    self.risk_metrics[vessel1.id].append(i / 180)       
            else:
                for vessel1 in dyn_env.vessels: 
                    self.risk_metrics[vessel1.id].append(self.risk_metrics[vessel1.id][-1])       
                    
                    
                    
    def will_collide(self, env: USVEnvironment, vessel1: Vessel):
        for vessel2 in env.vessels:
            if vessel2.id == vessel1.id:
                continue
            rel = Relation(vessel1, [MayCollide(True)], vessel2)
            if rel.collision_relations[0].get_penalty_norm() > 0.0:
                return True
        return False
                        
                    