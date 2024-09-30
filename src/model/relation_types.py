from abc import ABC, abstractmethod
from typing import List
import numpy as np
from model.environment.usv_config import BEAM_ANGLE, BOW_ANGLE, DIST_DRIFT, MASTHEAD_LIGHT_ANGLE, MAX_DISTANCE

class RelationType(ABC):
    def __init__(self, name : str, negated : bool, max_value : float) -> None:
        prefix = "!" if negated else ""
        self.name = prefix + name
        self.negated = negated
        self.max_value = max_value
    
    @abstractmethod
    def get_penalty_norm(self) -> float:
        pass
    
    def penalty(self, val, lb, ub) -> float:
        if not self.negated:
            dist = self._penalty(val, lb, ub)
        else:
            dist = min(self._penalty(val, -np.inf, lb), self._penalty(val, ub, np.inf))
        return self._normalize(dist, lb, ub)
    
    def _penalty(self, val, lb, ub):
        if val < lb:
            distance =  lb - val
        elif val > ub:
            distance = val - ub
        else:
            return 0.0
        return distance
    
    def _normalize(self, dist, lb, ub) -> float:
        return dist / (lb + self.max_value - ub)
    
   
    def set_relation(self, relation):
        from model.relation import Relation
        self.relation : Relation = relation
        
    def __repr__(self) -> str:
        return self.name
        
 
############ COLLISION ##################
class MayCollide(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'mayCollide', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        return self.penalty(self.relation.angle_v12_p12, 0, self.relation.angle_half_cone)
    
    
############ VISIBILITY DISTANCE ##################
class AtVis(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'atVis', negated, MAX_DISTANCE)
    
    def get_penalty_norm(self) -> float:
        return self.penalty(self.relation.o_distance, self.relation.vis_distance - DIST_DRIFT, self.relation.vis_distance + DIST_DRIFT)
    
class InVis(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'inVis', negated, MAX_DISTANCE)
    
    def get_penalty_norm(self) -> float:
        return self.penalty(self.relation.o_distance, self.relation.safety_dist, self.relation.vis_distance)
    
class OutVis(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'outVis', negated, MAX_DISTANCE)
    
    def get_penalty_norm(self) -> float:
        return self.penalty(self.relation.o_distance, self.relation.vis_distance, np.inf)
    
class OutVisOrNoCollide(OutVis, MayCollide):
    def __init__(self, negated : bool = False) -> None:
        self.outVis = OutVis(negated)
        self.may_collide = MayCollide(not negated)
        RelationType.__init__(self, f'({self.outVis.name} ∨ {self.may_collide.name})', negated, 0)
        
    def get_penalty_norm(self) -> float:
        if self.negated:
            return self.outVis.get_penalty_norm() + self.may_collide.get_penalty_norm()
        else:
            return min(self.outVis.get_penalty_norm(), self.may_collide.get_penalty_norm())
        
    def set_relation(self, relation):
        from model.relation import Relation
        self.relation : Relation = relation
        self.outVis.set_relation(relation)
        self.may_collide.set_relation(relation)
    
    
############ COLREG RELATIVE BEARING ##################
class CrossingBear(RelationType):
    rotation_angle = (BOW_ANGLE + BEAM_ANGLE) / 2
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'crossing', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        angle_p21_v2_rot = np.arccos(np.dot(self.relation.p21, self.rotated_v2()) / self.relation.o_distance / self.relation.vessel2.speed)
        return (self.penalty(angle_p21_v2_rot, 0.0, BEAM_ANGLE / 2.0)
                + self.penalty(self.relation.angle_p12_v1, 0, MASTHEAD_LIGHT_ANGLE /2))
        
    def rotated_v2(self):
        rotation_matrix = np.array([
            [np.cos(self.rotation_angle), -np.sin(self.rotation_angle)],
            [np.sin(self.rotation_angle), np.cos(self.rotation_angle)]
        ])
        # Rotate vector
        return np.dot(rotation_matrix, self.relation.vessel2.v)
    
class HeadOnBear(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'headOn', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        return (self.penalty(self.relation.angle_p21_v2, 0.0, BOW_ANGLE / 2.0)
                + self.penalty(self.relation.angle_p12_v1, 0.0, BOW_ANGLE / 2.0))
    
class OvertakingBear(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'overtaking', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        return (self.penalty(self.relation.angle_p21_v2, MASTHEAD_LIGHT_ANGLE / 2.0, np.pi)
                + self.penalty(self.relation.angle_p12_v1, 0, MASTHEAD_LIGHT_ANGLE /2))
        
        
        
def init_rel() -> List[RelationType]:
    return [MayCollide(), AtVis()]
def head_on_init() -> List[RelationType]:
    return init_rel() + [HeadOnBear()]
def crossing_init() -> List[RelationType]:
    return init_rel() + [CrossingBear()]
def overtaking_init() -> List[RelationType]:
    return init_rel() + [OvertakingBear()]
