
from abc import ABC, abstractmethod
from typing import Set
import numpy as np
from utils.asv_utils import BEAM_ANGLE, BOW_ANGLE, DIST_DRIFT, MASTHEAD_LIGHT_ANGLE, MAX_DISTANCE, MAX_LENGTH, MAX_SPEED_IN_MS
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache, GeometricProperties
from logical_level.models.penalty import Penalty
from logical_level.models.values import Values
from logical_level.models.actor_variable import ActorVariable, VesselVariable


class RelationConstrComposite(ABC):
    def __init__(self, components : Set['RelationConstrComposite']):
        super().__init__()
        self.components : Set['RelationConstrComposite'] = components
    
    @abstractmethod
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        pass
    
    def evaluate_penalty(self, assignments : Assignments) -> Penalty:
        cache = EvaluationCache(assignments)
        return self._evaluate_penalty(cache)
    
     
class RelationConstrTerm(RelationConstrComposite):
    def __init__(self, components : Set['RelationConstrComposite'] = set()):
        super().__init__(components)
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        return sum([comp._evaluate_penalty(eval_cache) for comp in self.components], Penalty())
    
    def __repr__(self) -> str:
        return f'({" ∧ ".join(f"{comp}" for comp in self.components)})'
    
    
class RelationConstrClause(RelationConstrComposite):
    def __init__(self, components : Set['RelationConstrComposite'] = set()):
        super().__init__(components)
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        return min([comp._evaluate_penalty(eval_cache) for comp in self.components])
    
    def __repr__(self) -> str:
        return f'({" ∨ ".join(f"{comp}" for comp in self.components)})'
    
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
    def __init__(self, var1 : ActorVariable, var2 : ActorVariable, literal_type, max_penalty, negated):
        super().__init__(literal_type, max_penalty, negated)
        self.var1 = var1
        self.var2 = var2
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        return self._do_evaluate_penalty(eval_cache.get_props(self.var1, self.var2))
        
    @abstractmethod
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        pass
    
    def __repr__(self) -> str:
        return f'{self.name}({self.var1}, {self.var2})'
 
class UnaryLiteral(Literal, ABC):
    def __init__(self, var : ActorVariable, literal_type, max_penalty, negated):
        super().__init__(literal_type, max_penalty, negated)
        self.var = var
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        values = eval_cache.assignments.get(self.var)
        return self._do_evaluate_penalty(values)
    
    @abstractmethod
    def _do_evaluate_penalty(self, value : Values) -> Penalty:
        pass
    
    def __repr__(self) -> str:
        return f'{self.name}({self.var})'
    
############ VISIBILITY DISTANCE ##################
class AtVis(BinaryLiteral):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'AtVis', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        penalty = self.penalty(geo_props.o_distance, geo_props.vis_distance - DIST_DRIFT, geo_props.vis_distance + DIST_DRIFT)
        return Penalty({self.var1 : penalty, self.var2 : penalty}, visibility_penalty=penalty,
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')
        
class InVis(BinaryLiteral):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'InVis', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        penalty = self.penalty(geo_props.o_distance, geo_props.safety_dist, geo_props.vis_distance)
        return Penalty({self.var1 : penalty, self.var2 : penalty}, visibility_penalty=penalty,
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')
        
class OutVis(BinaryLiteral):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'OutVis', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        penalty = self.penalty(geo_props.o_distance, max(geo_props.vis_distance, geo_props.safety_dist), MAX_DISTANCE)
        return Penalty({self.var1 : penalty, self.var2 : penalty}, visibility_penalty=penalty,
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')
        
        
############ COLREG RELATIVE BEARING ##################       
class CrossingBear(BinaryLiteral):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'CrossingBear', np.pi, negated)
        
    rotation_angle : float = (BOW_ANGLE + BEAM_ANGLE) / 2
        
    def __rotated_v2(self, geo_props : GeometricProperties):
        rotation_matrix = np.array([
            [np.cos(self.rotation_angle), -np.sin(self.rotation_angle)],
            [np.sin(self.rotation_angle), np.cos(self.rotation_angle)]
        ])
        # Rotate vector
        return np.dot(rotation_matrix, geo_props.val2.v)
        
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        angle_p21_v2_rot = np.arccos(np.dot(geo_props.p21, self.__rotated_v2(geo_props)) /
                                     geo_props.o_distance / geo_props.val2.sp)
        penalty = (self.penalty(angle_p21_v2_rot, 0.0, BEAM_ANGLE / 2.0) + self.penalty(geo_props.angle_p12_v1, 0.0, MASTHEAD_LIGHT_ANGLE / 2.0))
        return Penalty({self.var1 : penalty, self.var2 : penalty}, bearing_penalty=penalty,
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')
    
class HeadOnBear(BinaryLiteral):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'HeadOnBear', np.pi, negated)
        
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        penalty = self.penalty(geo_props.angle_p21_v2, 0.0, BOW_ANGLE / 2.0) + self.penalty(geo_props.angle_p12_v1, 0.0, BOW_ANGLE / 2.0)
        return Penalty({self.var1 : penalty, self.var2 : penalty}, bearing_penalty=penalty,
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')
    
class OvertakingBear(BinaryLiteral):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'OvertakingBear', np.pi, negated)
        
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        penalty = self.penalty(geo_props.angle_p21_v2, MASTHEAD_LIGHT_ANGLE / 2.0, np.pi) + self.penalty(geo_props.angle_p12_v1, 0.0, MASTHEAD_LIGHT_ANGLE / 2.0)
        return Penalty({self.var1 : penalty, self.var2 : penalty}, bearing_penalty=penalty,
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')
    
    
    
############ MAY COLLISION ##################
class MayCollide(BinaryLiteral):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'MayCollide', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        penalty = self.penalty(geo_props.dcpa, 0, geo_props.safety_dist)
        return Penalty({self.var1 : penalty, self.var2 : penalty}, collision_penalty=penalty,
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')
    
############ COLLISION ##################
class DoCollide(BinaryLiteral):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable, negated : bool = False):
        super().__init__(var1, var2, 'DoCollide', MAX_DISTANCE, negated)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        penalty = self.penalty(geo_props.o_distance, 0, geo_props.safety_dist)
        return Penalty({self.var1 : penalty, self.var2 : penalty}, collision_penalty=penalty,
                       info=fr'{self.name}({self.var1, self.var2}) : {penalty}')    
    
class LengthLiteral(UnaryLiteral):
    def __init__(self, var : VesselVariable, negated : bool = False):
        super().__init__(var, 'Length', MAX_LENGTH, negated)
        self.var : VesselVariable = var
    
    def _do_evaluate_penalty(self, values : Values) -> Penalty:
        penalty = self.penalty(values.l, self.var.min_length, self.var.max_length)
        return Penalty({self.var : penalty}, dimension_penalty=penalty,
                       info=fr'{self.name}({self.var}) : {penalty}')
    
class SpeedLiteral(UnaryLiteral):
    def __init__(self, var : VesselVariable, negated : bool = False):
        super().__init__(var, 'Speed', MAX_SPEED_IN_MS, negated)
        self.var : VesselVariable = var
    
    def _do_evaluate_penalty(self, values : Values) -> Penalty:
        penalty = self.penalty(values.sp, self.var.min_speed, self.var.max_speed)
        return Penalty({self.var : penalty}, dimension_penalty=penalty,
                       info=fr'{self.name}({self.var}) : {penalty}')
    