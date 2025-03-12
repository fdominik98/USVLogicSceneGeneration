from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache, GeometricProperties
from logical_level.models.actor_variable import ActorVariable, VesselVariable
from logical_level.models.penalty import Penalty, PenaltyCategory
from logical_level.models.relation_constraints_concept.composites import RelationConstrComposite
from logical_level.models.values import ActorValues, VesselValues
from utils.asv_utils import BEAM_ANGLE, BOW_ANGLE, DIST_DRIFT, MASTHEAD_LIGHT_ANGLE, MAX_DISTANCE, MAX_LENGTH, MAX_SPEED_IN_MS


class Literal(RelationConstrComposite, ABC):   
    def __init__(self, literal_type : str, max_penalty, negated):
        super().__init__(components=set())
        self.literal_type = literal_type
        self.max_penalty = max_penalty
        self.negated = negated
    
    @property
    def name(self):
        prefix = "!" if self.negated else ""
        return prefix + self.literal_type
    
    @abstractmethod
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        pass  
    
    def penalty(self, val, lb, ub) -> float:
        if not self.negated:
            dist = self._penalty(val, lb, ub)
            return self._normalize(dist, lb, ub)
        else:
            dist1 = self._penalty(val, 0, lb)
            dist2 = self._penalty(val, ub, self.max_penalty)
            return min(self._normalize(dist1, 0, lb), self._normalize(dist2, ub, self.max_penalty))
    
    def _penalty(self, val, lb, ub):
        if val < lb:
            distance =  lb - val
        elif val > ub:
            distance = val - ub
        else:
            return 0.0
        return distance
    
    def _normalize(self, dist, lb, ub) -> float:
        return dist / (max(lb, self.max_penalty - ub))
    
class BinaryLiteral(Literal, ABC):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, literal_type, max_penalty, negated):
        super().__init__(literal_type, max_penalty, negated)
        self.var1 : ActorVariable = var1
        self.var2 : VesselVariable = var2
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        category, penalty = self._do_evaluate_penalty(eval_cache.get_props(self.var1, self.var2))
        return Penalty({self.var1 : penalty, self.var2 : penalty}, **{category : penalty},
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')
        
    @abstractmethod
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        pass
    
    def __repr__(self) -> str:
        return f'{self.name}({self.var1}, {self.var2})'
 
class UnaryLiteral(Literal, ABC):
    def __init__(self, var : ActorVariable, literal_type, max_penalty, negated):
        super().__init__(literal_type, max_penalty, negated)
        self.var : ActorVariable = var
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        values = eval_cache.assignments.get(self.var)
        category, penalty = self._do_evaluate_penalty(values)
        return Penalty({self.var : penalty}, **{category : penalty},
                       info=fr'{self.name}({self.var}) : {penalty}')
    
    @abstractmethod
    def _do_evaluate_penalty(self, value : ActorValues) -> Tuple[PenaltyCategory, float]:
        pass
    
    def __repr__(self) -> str:
        return f'{self.name}({self.var})'
    
############ VISIBILITY DISTANCE ##################
class AtVis(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'AtVis', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        return PenaltyCategory.VISIBILITY, self.penalty(geo_props.o_distance, geo_props.vis_distance - DIST_DRIFT, geo_props.vis_distance + DIST_DRIFT)
        
class InVis(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'InVis', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        return PenaltyCategory.VISIBILITY, self.penalty(geo_props.o_distance, geo_props.safety_dist, geo_props.vis_distance - DIST_DRIFT)
        
class OutVis(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'OutVis', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        return PenaltyCategory.VISIBILITY, self.penalty(geo_props.o_distance, max(geo_props.vis_distance + DIST_DRIFT, geo_props.safety_dist), MAX_DISTANCE)
        
        
############ RELATIVE BEARING ##################       
class InPortSectorOf(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'InPortSectorOf', np.pi, negated)
        
    rotation_angle : float = BEAM_ANGLE / 2
    rotation_matrix = np.array([
        [np.cos(rotation_angle), -np.sin(rotation_angle)],
        [np.sin(rotation_angle), np.cos(rotation_angle)]
    ])
        
    def __rotated_v2(self, geo_props : GeometricProperties):
        return np.dot(self.rotation_matrix, geo_props.val2.v)
            
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        angle_p21_v2_rot = np.arccos(np.dot(geo_props.p21, self.__rotated_v2(geo_props)) /
                                     geo_props.o_distance / geo_props.val2.sp)
        return PenaltyCategory.BEARING, (self.penalty(angle_p21_v2_rot, 0.0, BEAM_ANGLE / 2.0))
    
class InStarboardSectorOf(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'InStarboardSectorOf', np.pi, negated)
        
    rotation_angle : float = BEAM_ANGLE / 2
    rotation_matrix = np.array([
        [np.cos(-rotation_angle), -np.sin(-rotation_angle)],
        [np.sin(-rotation_angle), np.cos(-rotation_angle)]
    ])
        
    def __rotated_v2(self, geo_props : GeometricProperties):
        return np.dot(self.rotation_matrix, geo_props.val2.v)
        
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        angle_p21_v2_rot = np.arccos(np.dot(geo_props.p21, self.__rotated_v2(geo_props)) /
                                     geo_props.o_distance / geo_props.val2.sp)
        return PenaltyCategory.BEARING, (self.penalty(angle_p21_v2_rot, 0.0, BEAM_ANGLE / 2.0))
        
class InHeadOnSectorOf(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'InHeadOnSectorOf', np.pi, negated)
        
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        sin_half_cone_p21_theta = np.clip(geo_props.val1.r / geo_props.o_distance, -1, 1)
        angle_half_cone_p21 = abs(np.arcsin(sin_half_cone_p21_theta))
        return PenaltyCategory.BEARING, self.penalty(geo_props.angle_p21_v2, 0.0, max(angle_half_cone_p21, BOW_ANGLE))
    
class InSternSectorOf(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'InSternSectorOf', np.pi, negated)
        
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        return PenaltyCategory.BEARING, self.penalty(geo_props.angle_p21_v2, MASTHEAD_LIGHT_ANGLE / 2.0, np.pi)
    
    
############ MAY COLLISION ##################
class MayCollide(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'MayCollide', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        return PenaltyCategory.COLLISION, self.penalty(geo_props.dcpa, 0, geo_props.safety_dist)
    
############ COLLISION ##################
class DoCollide(BinaryLiteral):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'DoCollide', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Tuple[PenaltyCategory, float]:
        return PenaltyCategory.COLLISION, self.penalty(geo_props.o_distance, 0, geo_props.safety_dist)
    
############ DIMENSION ##################
class LengthLiteral(UnaryLiteral):
    def __init__(self, var : VesselVariable, negated : bool = False):
        super().__init__(var, 'Length', MAX_LENGTH, negated)
        self.var : VesselVariable
    
    def _do_evaluate_penalty(self, values : VesselValues) -> Tuple[PenaltyCategory, float]:
        return PenaltyCategory.DIMENSION, self.penalty(values.l, self.var.min_length, self.var.max_length)
    
class SpeedLiteral(UnaryLiteral):
    def __init__(self, var : VesselVariable, negated : bool = False):
        super().__init__(var, 'Speed', MAX_SPEED_IN_MS, negated)
        self.var : VesselVariable
        
    def _do_evaluate_penalty(self, values : VesselValues) -> Tuple[PenaltyCategory, float]:
        return PenaltyCategory.DIMENSION, self.penalty(values.sp, self.var.min_speed, self.var.max_speed)
    