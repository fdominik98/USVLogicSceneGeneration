from typing import Dict, List, Tuple
from model.environment.usv_environment import USVEnvironment
import copy
from model.relation import Relation
from evaluation.risk_evaluation import NavigationRiskVector, ProximityRiskVector

class TrajProximityMetric():
    def __init__(self, relation : Relation) -> None:
        self.vectors : List[ProximityRiskVector] = []
        self.len = 0
        self.relation = relation
        
    def append(self, pv : ProximityRiskVector):
        self.vectors.append(pv)
        self.len += 1
        
    def get_first_dcpa(self) -> float:
        return self.vectors[0].dcpa
    
    def get_first_distance(self) -> float:
        return self.vectors[0].dist
    
    def get_first_tcpa(self) -> float:
        return self.vectors[0].tcpa

class TrajProximityEvaluator():
    def __init__(self, env : USVEnvironment, trajectories: Dict[int, List[Tuple[float,float,float,float]]]) -> None:
        self.env = env
        self.trajectories = trajectories
        self.metrics : List[TrajProximityMetric] = []
        
        for relation in env.relations:
            if relation.has_os():
                self.metrics.append(self.calculate_pair(relation))
        
    def calculate_pair(self, relation : Relation) -> TrajProximityMetric:
        dyn_rel = copy.deepcopy(relation)
        v1 = dyn_rel.vessel1
        v2 = dyn_rel.vessel2
        
        traj1 = self.trajectories[v1.id]
        traj2 = self.trajectories[v2.id]
        
        metrics = TrajProximityMetric(relation)
        for s, (pos1, pos2) in enumerate(zip(traj1, traj2)):
            v1.update(*pos1)
            v2.update(*pos2)
            dyn_rel.update()
            metrics.append(ProximityRiskVector(dyn_rel))
            
        return metrics
    
class TrajNavigationRiskEvaluator():
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
                    
                for o in dyn_env.vessels:    
                    risk_vector = NavigationRiskVector(dyn_env, o)               
                    self.risk_metrics[o.id].append(risk_vector.find_minimum_turning_metric())       
            else:
                for o in dyn_env.vessels: 
                    self.risk_metrics[o.id].append(self.risk_metrics[o.id][-1])       
                    
                    
                    
    