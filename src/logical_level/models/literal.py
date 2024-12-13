
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Set
import numpy as np
from asv_utils import BEAM_ANGLE, BOW_ANGLE, DIST_DRIFT, MASTHEAD_LIGHT_ANGLE, MAX_DISTANCE
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache, GeometricProperties
from logical_level.models.penalty import Penalty
from logical_level.models.vessel_variable import ActorVariable


dataclass(frozen=True)
class RelationConstrComposite(ABC):
    components : Set['RelationConstrComposite'] = field(default_factory=set)
    
    @abstractmethod
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        pass
    
    def evaluate_penalty(self, assignments : Assignments) -> Penalty:
        cache = EvaluationCache(assignments)
        return self._evaluate_penalty(cache)
    
     
dataclass(frozen=True)   
class RelationConstrTerm(RelationConstrComposite):
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        return sum([comp._evaluate_penalty(eval_cache) for comp in self.components])
    
    def __repr__(self) -> str:
        return " ∧ ".join(f"({comp})" for comp in self.components)
    
    
dataclass(frozen=True)    
class RelationConstrClause(RelationConstrComposite):
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        return min([comp._evaluate_penalty(eval_cache) for comp in self.components])
    
    def __repr__(self) -> str:
        return " ∨ ".join(f"({comp})" for comp in self.components)
    

dataclass(frozen=True)
class Literal(ABC, RelationConstrComposite):
    var1 : ActorVariable
    var2 : ActorVariable
    literal_type : str
    max_value : float
    negated : bool = False
    components : Set[RelationConstrComposite] = field(default_factory=set, init=False)
    
    @property
    def name(self):
        prefix = "!" if self.negated else ""
        return prefix + self.literal_type
    
    def __repr__(self) -> str:
        return f'{self.name}({self.var1}, {self.var2})'
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        return self._do_evaluate_penalty(eval_cache.get_props(self.var1, self.var2))
        
    @abstractmethod
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
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
    
    
############ VISIBILITY DISTANCE ##################
@dataclass(frozen=True)
class AtVis(Literal):
    literal_type : str = field(default='AtVis', init=False)
    max_value : float = field(default=MAX_DISTANCE, init=False)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        value = self.penalty(geo_props.o_distance, geo_props.vis_distance - DIST_DRIFT, geo_props.vis_distance + DIST_DRIFT)
        return Penalty([value], [], [], {self.var1 : value, self.var2 : value})
        
@dataclass(frozen=True)
class InVis(Literal):
    literal_type : str = field(default='InVis', init=False)
    max_value : float = field(default=MAX_DISTANCE, init=False)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        value = self.penalty(geo_props.o_distance, geo_props.safety_dist, geo_props.vis_distance)
        return Penalty([value], [], [], {self.var1 : value, self.var2 : value})
        
@dataclass(frozen=True)
class OutVis(Literal):
    literal_type : str = field(default='OutVis', init=False)
    max_value : float = field(default=MAX_DISTANCE, init=False)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        value = self.penalty(geo_props.o_distance, max(geo_props.vis_distance, geo_props.safety_dist), MAX_DISTANCE)
        return Penalty([value], [], [], {self.var1 : value, self.var2 : value})
        
        
############ COLREG RELATIVE BEARING ##################       
dataclass(frozen=True)
class CrossingBear(Literal):
    literal_type : str = field(default='CrossingBear', init=False)
    max_value : float = field(default=np.pi, init=False)
    rotation_angle : float = field(default=(BOW_ANGLE + BEAM_ANGLE) / 2, init=False)
        
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
        value = (self.penalty(angle_p21_v2_rot, 0.0, BEAM_ANGLE / 2.0) + self.penalty(geo_props.angle_p12_v1, 0.0, MASTHEAD_LIGHT_ANGLE / 2.0))
        return Penalty([], [value], [], {self.var1 : value, self.var2 : value})
    
    
dataclass(frozen=True)
class HeadOnBear(Literal):
    literal_type : str = field(default='HeadOnBear', init=False)
    max_value : float = field(default=np.pi, init=False)
        
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        value = self.penalty(geo_props.angle_p21_v2, 0.0, BOW_ANGLE / 2.0) + self.penalty(geo_props.angle_p12_v1, 0.0, BOW_ANGLE / 2.0)
        return Penalty([], [value], [], {self.var1 : value, self.var2 : value})
        
dataclass(frozen=True)
class OvertakingBear(Literal):
    literal_type : str = field(default='OvertakingBear', init=False)
    max_value : float = field(default=np.pi, init=False)
        
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        value = self.penalty(geo_props.angle_p21_v2, MASTHEAD_LIGHT_ANGLE / 2.0, np.pi) + self.penalty(geo_props.angle_p12_v1, 0.0, MASTHEAD_LIGHT_ANGLE / 2.0)
        return Penalty([], [value], [], {self.var1 : value, self.var2 : value})
    
    
    
############ COLLISION ##################
dataclass(frozen=True)
class MayCollide(Literal):
    literal_type : str = field(default='MayCollide', init=False)
    max_value : float = field(default=np.pi, init=False)
    
    def _do_evaluate_penalty(self, geo_props : GeometricProperties) -> Penalty:
        value = self.penalty(geo_props.dcpa, 0, geo_props.safety_dist)
        return Penalty([], [], [value], {self.var1 : value, self.var2 : value})
    