from typing import Dict, List, Tuple

import numpy as np
from model.environment.usv_environment import USVEnvironment
from model.vessel import Vessel
import copy

from model.colreg_situation import Relation, NoColreg

class ProximityMetrics():
    def __init__(self, colreg_s : Relation, closest_index : int, closest_dist : np.ndarray) -> None:
        self.distances : List[float] = []
        self.dcpas : List[float] = [] # Distance at the Closest Point of Approach
        self.tcpas : List[float] = [] # Time to the Closest Point of Approach
        self.len = 0
        self.closest_index = closest_index
        self.closest_dist = closest_dist
        self.colreg_s = colreg_s
        
    def append(self, dist, dcpa, tcpa):
        self.distances.append(dist)
        self.dcpas.append(dcpa)
        self.tcpas.append(tcpa)
        self.len += 1
        
    def get_first_dcpa(self) -> float:
        return self.dcpas[0]
    
    def get_first_distance(self) -> float:
        return self.distances[0]
    
    def get_first_tcpa(self) -> float:
        return self.tcpas[0]

class ProximityEvaluator():
    def __init__(self, env : USVEnvironment, trajectories: Dict[int, List[Tuple[float,float,float,float]]]) -> None:
        self.env = env
        self.trajectories = trajectories
        self.metrics : List[ProximityMetrics] = []
        
        for colreg_s in env.colreg_situations:
            if colreg_s.vessel1.is_OS() or colreg_s.vessel2.is_OS():
                self.metrics.append(self.calculate_pair(colreg_s))
        
    def calculate_pair(self, colreg_s : Relation) -> ProximityMetrics:
        dyn_colreg_s = copy.deepcopy(colreg_s)
        v1 = dyn_colreg_s.vessel1
        v2 = dyn_colreg_s.vessel2
        
        traj1 = self.trajectories[v1.id]
        traj2 = self.trajectories[v2.id]
        closest_index, closest_pos1, closest_pos2 = self.find_closest_positions(traj1, traj2)
        
        metrics = ProximityMetrics(colreg_s, closest_index, closest_pos1)
        for s, (pos1, pos2) in enumerate(zip(traj1, traj2)):
            v1.update(*pos1)
            v2.update(*pos2)
            dyn_colreg_s.update()
            dist = dyn_colreg_s.o_distance
            theta = np.pi - colreg_s.angle_v12_p12
            dcpa = dist * abs(np.sin(theta))
            tcpa = -dist * np.cos(theta) / np.linalg.norm(colreg_s.v12)
            metrics.append(dist, dcpa, tcpa)
            
        return metrics
    
    def find_closest_positions(self, traj1 : List[Tuple[float,float,float,float]], traj2 : List[Tuple[float,float,float,float]]) -> Tuple[int, np.ndarray, np.ndarray]:
        min_diff = float('inf')  # Initialize with a large number
        closest_index = -1  # Index of the closest positions
        closest_position1 = np.array([0,0])
        closest_position2 = np.array([0,0])

        for i in range(len(traj1)):
            dist = np.sqrt((traj1[i][0] - traj2[i][0])**2 + (traj1[i][1] - traj2[i][1])**2)
            if dist < min_diff:
                min_diff = dist
                closest_index = i
                closest_position1 = np.array([traj1[i][0], traj1[i]][1])
                closest_position2 = np.array([traj2[i][0], traj2[i]][1])

        return closest_index, closest_position1, closest_position2
    
    
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
                    for i in range(0, 180, 2):
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
            colreg = NoColreg(vessel1, vessel2)
            if colreg.get_penalties()[1][0] > 0.0:
                return True
        return False
                        
                    