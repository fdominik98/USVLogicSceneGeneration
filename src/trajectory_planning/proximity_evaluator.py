from typing import Dict, List, Tuple

import numpy as np
from model.usv_environment import USVEnvironment
from model.vessel import Vessel
import copy

from model.colreg_situation import ColregSituation

class DynamicMetrics():
    def __init__(self, colreg_s : ColregSituation, closest_index : int, closest_dist : np.ndarray) -> None:
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
        self.metrics : List[DynamicMetrics] = []
        
        for colreg_s in env.colreg_situations:
            if colreg_s.vessel1.id == 0 or colreg_s.vessel2.id == 0:
                self.metrics.append(self.calculate_pair(colreg_s))
        
    def calculate_pair(self, colreg_s : ColregSituation) -> DynamicMetrics:
        dyn_colreg_s = copy.deepcopy(colreg_s)
        ego_vessel = dyn_colreg_s.vessel1 if dyn_colreg_s.vessel1.id == 0 else dyn_colreg_s.vessel2
        other_vessel = dyn_colreg_s.vessel1 if dyn_colreg_s.vessel1.id != 0 else dyn_colreg_s.vessel2
        
        traj1 = self.trajectories[ego_vessel.id]
        traj2 = self.trajectories[other_vessel.id]
        closest_index, closest_pos1, closest_pos2 = self.find_closest_positions(traj1, traj2)
        
        metrics = DynamicMetrics(colreg_s, closest_index, closest_pos1)
        for s, (pos1, pos2) in enumerate(zip(traj1, traj2)):
            ego_vessel.update(*pos1)
            other_vessel.update(*pos2)
            dyn_colreg_s.update()
            dist = dyn_colreg_s.o_distance
            dcpa = np.linalg.norm(closest_pos1[:2] - np.array(pos1[:2]))
            tcpa = closest_index - s
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