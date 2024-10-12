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
            return self._normalize(dist, lb, ub)
        else:
            dist1 = self._penalty(val, 0, lb)
            dist2 = self._penalty(val, ub, self.max_value)
            return min(self._normalize(dist1, 0, lb), self._normalize(dist2, ub, self.max_value))
    
    def _penalty(self, val, lb, ub):
        if val < lb:
            distance =  lb - val
        elif val > ub:
            distance = val - ub
        else:
            return 0.0
        return distance
    
    def _normalize(self, dist, lb, ub) -> float:
        return dist / (max(lb, self.max_value - ub))
    
    @abstractmethod
    def is_bidir(self) -> bool:
        pass    
   
    def set_relation(self, relation):
        from model.relation import Relation
        self.relation : Relation = relation
        
    def __repr__(self) -> str:
        return self.name
        
class RelationTypeDisj(RelationType, ABC):
    def __init__(self, relations : List[RelationType], negated = False) -> None:
        self.relations : List[RelationType] = relations
        RelationType.__init__(self, f'({" V ".join([r.name for r in self.relations])})', negated, 0)
        
    def get_penalty_norm(self) -> float:
        penalty_norms = [r.get_penalty_norm() for r in self.relations]
        if self.negated:
            return sum(penalty_norms)
        else:
            return min(penalty_norms)
    
    def set_relation(self, relation):
        from model.relation import Relation
        self.relation : Relation = relation
        for rel in self.relations:
            rel.set_relation(relation)
            
    def is_bidir(self) -> bool:
        return all(rel.is_bidir() for rel in self.relations)
 
############ COLLISION ##################
class MayCollide(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'mayCollide', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        return self.penalty(self.relation.angle_v12_p12, 0, self.relation.angle_half_cone)
    
    def is_bidir(self) -> bool:
        return True
    
    
############ VISIBILITY DISTANCE ##################
class AtVis(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'atVis', negated, MAX_DISTANCE)
    
    def get_penalty_norm(self) -> float:
        return self.penalty(self.relation.o_distance, self.relation.vis_distance - DIST_DRIFT, self.relation.vis_distance + DIST_DRIFT)
    
    def is_bidir(self) -> bool:
        return True
    
class InVis(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'inVis', negated, MAX_DISTANCE)
    
    def get_penalty_norm(self) -> float:
        return self.penalty(self.relation.o_distance, self.relation.safety_dist, self.relation.vis_distance)
    
    def is_bidir(self) -> bool:
        return True
    
class OutVis(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'outVis', negated, MAX_DISTANCE)
    
    def get_penalty_norm(self) -> float:
        lb = max(self.relation.vis_distance, self.relation.safety_dist)
        return self.penalty(self.relation.o_distance, lb, MAX_DISTANCE)
    
    def is_bidir(self) -> bool:
        return True
    
class OutVisOrNoCollide(RelationTypeDisj, OutVis, MayCollide):
    def __init__(self, negated : bool = False) -> None:
        RelationTypeDisj.__init__(self, [OutVis(negated), MayCollide(not negated)], negated)       
    
    
############ COLREG RELATIVE BEARING ##################
class CrossingBear(RelationType):
    rotation_angle = (BOW_ANGLE + BEAM_ANGLE) / 2
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'crossing', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        angle_p21_v2_rot = np.arccos(np.dot(self.relation.p21, self.rotated_v2()) / self.relation.o_distance / self.relation.vessel2.speed)
        return (self.penalty(angle_p21_v2_rot, 0.0, BEAM_ANGLE / 2.0)
                + self.penalty(self.relation.angle_p12_v1, 0.0, MASTHEAD_LIGHT_ANGLE / 2.0))
        
    def rotated_v2(self):
        rotation_matrix = np.array([
            [np.cos(self.rotation_angle), -np.sin(self.rotation_angle)],
            [np.sin(self.rotation_angle), np.cos(self.rotation_angle)]
        ])
        # Rotate vector
        return np.dot(rotation_matrix, self.relation.vessel2.v)
    
    def is_bidir(self) -> bool:
        return False
    
class HeadOnBear(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'headOn', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        return (self.penalty(self.relation.angle_p21_v2, 0.0, BOW_ANGLE / 2.0)
                + self.penalty(self.relation.angle_p12_v1, 0.0, BOW_ANGLE / 2.0))
        
    def is_bidir(self) -> bool:
        return True
    
class OvertakingBear(RelationType):
    def __init__(self, negated : bool= False) -> None:
        RelationType.__init__(self, 'overtaking', negated, np.pi)
    
    def get_penalty_norm(self) -> float:
        return (self.penalty(self.relation.angle_p21_v2, MASTHEAD_LIGHT_ANGLE / 2.0, np.pi)
                + self.penalty(self.relation.angle_p12_v1, 0.0, MASTHEAD_LIGHT_ANGLE / 2.0))
        
    def is_bidir(self) -> bool:
        return False
        
class AnyColregBear(RelationTypeDisj, HeadOnBear, OvertakingBear, CrossingBear):
    def __init__(self, negated : bool = False) -> None:
        RelationTypeDisj.__init__(self, [HeadOnBear(negated), OvertakingBear(negated), CrossingBear(negated)], negated)
        
class OvertakingOrCrossingBear(RelationTypeDisj, OvertakingBear, CrossingBear):
    def __init__(self, negated : bool = False) -> None:
        RelationTypeDisj.__init__(self, [OvertakingBear(negated), CrossingBear(negated)], negated)
        
        
def may_collide_at_vis() -> List[RelationType]:
    return [MayCollide(), AtVis()]
def head_on_init() -> List[RelationType]:
    return may_collide_at_vis() + [HeadOnBear()]
def crossing_init() -> List[RelationType]:
    return may_collide_at_vis() + [CrossingBear()]
def overtaking_init() -> List[RelationType]:
    return may_collide_at_vis() + [OvertakingBear()]

def any_colreg_init() -> List[RelationType]:
    return may_collide_at_vis() + [AnyColregBear()]

def overtaking_or_crossing_init() -> List[RelationType]:
    return may_collide_at_vis() + [OvertakingOrCrossingBear()]
