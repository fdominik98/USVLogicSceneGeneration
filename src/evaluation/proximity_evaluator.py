from typing import Dict, List, Tuple
from logical_level.models.logical_scenario import LogicalScenario
import copy
from logical_level.models.relation_constraint import RelationConstr
from evaluation.risk_evaluation import RiskVector, ProximityRiskIndex, NavigationRiskIndex

class TrajProximityMetric():
    def __init__(self, relation : RelationConstr) -> None:
        self.vectors : List[ProximityRiskIndex] = []
        self.len = 0
        self.relation = relation
        
    def append(self, pv : ProximityRiskIndex):
        self.vectors.append(pv)
        self.len += 1
        
    def get_first_dcpa(self) -> float:
        return self.vectors[0].dcpa
    
    def get_first_distance(self) -> float:
        return self.vectors[0].dist
    
    def get_first_tcpa(self) -> float:
        return self.vectors[0].tcpa

class TrajProximityEvaluator():
    def __init__(self,logical_scenario: LogicalScenario, trajectories: Dict[int, List[Tuple[float, float, float, float, float]]]) -> None:
        self.logical_scenario = env
        self.trajectories = trajectories
        self.metrics : List[TrajProximityMetric] = []
        
        for relation in env.relations:
            if relation.has_os():
                self.metrics.append(self.calculate_pair(relation))
        
    def calculate_pair(self, relation : RelationConstr) -> TrajProximityMetric:
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
            metrics.append(ProximityRiskIndex(dyn_rel))
            
        return metrics
    
class TrajNavigationRiskEvaluator():
    def __init__(self,logical_scenario: LogicalScenario, trajectories: Dict[int, List[Tuple[float, float, float, float, float]]]) -> None:
        self.logical_scenario = env
        self.trajectories = trajectories
        self.danger_sector_metrics : Dict[int, List[float]] = {v.id : [] for v in env.vessel_vars}
        self.proximity_metrics : Dict[int, List[float]] = {v.id : [] for v in env.vessel_vars}
        
        dyn_env = copy.deepcopy(env)
        
        for t in range(len(trajectories[0])):
            if t % 30 == 0:                    
                for o in dyn_env.vessel_vars: ## TODO MAKE IT SIMPLER
                    traj = trajectories[o.id]
                    o.update(*(traj[t]))
                for rel in dyn_env.relations:
                    rel.update()
                for o in dyn_env.vessel_vars: 
                    if not o.is_OS():
                        continue   
                    risk_vector = RiskVector(env=dyn_env)
                    self.danger_sector_metrics[o.id].append(risk_vector.danger_sector)
                    self.proximity_metrics[o.id].append(risk_vector.max_proximity_index.proximity_index)      
            else:
                for o in dyn_env.vessel_vars: 
                    if not o.is_OS():
                        continue 
                    self.danger_sector_metrics[o.id].append(self.danger_sector_metrics[o.id][-1])
                    self.proximity_metrics[o.id].append(self.proximity_metrics[o.id][-1])      
                    
                    
                    
    