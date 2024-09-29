from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
from model.environment.usv_config import BEAM_ANGLE, BOW_ANGLE, DIST_DRIFT, MASTHEAD_LIGHT_ANGLE, MAX_DISTANCE, vector_angle_diff
from model.relation import Relation


class RelationType(ABC):
    def __init__(self, name : str, negated : bool, max_value : float) -> None:
        self.name = name
        self.negated = negated
        self.max_value = max_value
    
    @abstractmethod
    def get_penalty_norm(self) -> float:
        pass
    
    def penalty(self, val, lb, ub) -> float:
        if not self.negated:
            dist = self._penalty(val, lb, ub)
        else:
            dist = min(self._penalty(val, 0, lb), self._penalty(val, ub, 1))
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
    
   
    def set_relation(self, relation : Relation):
        self.relation = relation
        
 
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
        return self.penalty(self.relation.o_distance, 0, self.relation.vis_distance)
    
class OutVis(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'outVis', negated, MAX_DISTANCE)
    
    def get_penalty_norm(self) -> float:
        return self.penalty(self.relation.o_distance, self.relation.vis_distance, np.inf)
    
    
############ COLREG RELATIVE BEARING ##################
class CrossingBear(RelationType):
    rotation_angle = (BOW_ANGLE + BEAM_ANGLE) / 2
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'crossing', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        angle_p21_v2_rot = vector_angle_diff(self.rotated_v2(), self.relation.p21_heading)
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
        
        
INIT_REL = [MayCollide(), AtVis()]
HEAD_ON_INIT = INIT_REL + [HeadOnBear()]
CROSSING_INIT = INIT_REL + [CrossingBear()]
OVERTAKING_INIT = INIT_REL + [OvertakingBear()]
IN_VIS = [MayCollide(False), InVis()]
