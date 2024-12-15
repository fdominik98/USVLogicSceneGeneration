import numpy as np
from typing import List
from asv_utils import EPSILON, o2VisibilityByo1, N_MILE_TO_M_CONVERSION
from logical_level.models.constraint_types import AtVis, CrossingBear, HeadOnBear, InVis, MayCollide, OutVis, OutVisOrNoCollide, OvertakingBear, ConstraintType
from logical_level.models.actor_variable import ActorVariable
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.values import Values


class RelationConstr():
    def __init__(self, vessel1 : ActorVariable, relation_types : List[ConstraintType], vessel2 : ActorVariable) -> None:
        self.vessel1 = vessel1
        self.vessel2 = vessel2
        self.short_name = f'{self.vessel1.id} -> {self.vessel2.id}'
        self.relation_types : List[ConstraintType] = []
        self.collision_relations : List[ConstraintType] = []
        self.visibility_relations : List[ConstraintType] = []
        self.bearing_relations : List[ConstraintType] = []
        
        for r in relation_types:
            r.set_relation(self)
            if isinstance(r, MayCollide):
                self.collision_relations.append(r)
            if isinstance(r, AtVis) or isinstance(r, InVis) or isinstance(r, OutVis):
                self.visibility_relations.append(r)
            if isinstance(r, HeadOnBear) or isinstance(r, CrossingBear) or isinstance(r, OvertakingBear):
                self.bearing_relations.append(r)
            self.relation_types.append(r)
            
        self.name = rf'{self.vessel1} - ({", ".join([r.name for r in self.relation_types])}) -> {self.vessel2}'
        
    def has_os(self)-> bool:
        return self.vessel1.is_os or self.vessel2.is_os
    
    def no_colreg(self) -> bool:
        for rel in self.collision_relations:
            if isinstance(rel, MayCollide) and not isinstance(rel, OutVisOrNoCollide) and not rel.negated:
                return True
        return False
    
    def has_head_on(self) -> bool:
        for rel in self.bearing_relations:
            if isinstance(rel, HeadOnBear) and not rel.negated:
                return True
        return False
        
    def __repr__(self) -> str:
        return self.name
    
    def get_penalty_norms(self):
        return [rel.get_penalty_norm() for rel in self.visibility_relations], [rel.get_penalty_norm() for rel in self.bearing_relations], [rel.get_penalty_norm() for rel in self.collision_relations]
           
    def update(self, assignments : Assignments):
        val1 : Values = assignments(self.vessel1)
        val2 : Values = assignments(self.vessel2)
        self.safety_dist = max(val1.r, val2.r)
        self.p12 = val2.p - val1.p
        self.p21 = val1.p - val2.p
        self.v12 = val1.v - val2.v
        
        # Define the norm of the relative position (distance(p1 p2))
        self.o_distance = max(np.linalg.norm(self.p12), EPSILON)   
        
        self.cos_p21_v2_theta = np.clip(np.dot(self.p21, val2.v) / self.o_distance / val2.sp, -1, 1)
        self.angle_p21_v2 = np.arccos(self.cos_p21_v2_theta)        
        self.cos_p12_v1_theta = np.clip(np.dot(self.p12, val1.v) / self.o_distance / val1.sp, -1, 1)
        self.angle_p12_v1 = np.arccos(self.cos_p12_v1_theta)
        
        self.vis_distance = min(o2VisibilityByo1(self.angle_p12_v1, val1.l),
                           o2VisibilityByo1(self.angle_p21_v2, val2.l)) *  N_MILE_TO_M_CONVERSION
        # angle between the relative velocity and the relative position vector
        
        self.v12_norm_stable = max(np.linalg.norm(self.v12), EPSILON)
        self.dot_p12_v12 = np.dot(self.p12, self.v12)
        #self.cos_p12_v12_theta = np.clip(self.dot_p12_v12 / self.o_distance / self.v12_norm_stable, -1, 1)
        #self.angle_v12_p12 = np.arccos(self.cos_p12_v12_theta)
        
        self.tcpa = self.dot_p12_v12 / self.v12_norm_stable**2
        self.dcpa = np.linalg.norm(self.p21 + self.v12 * max(0, self.tcpa)) 
        
        self.cat_penalties = self.get_penalty_norms()
        self.penalties_sum = sum(penalty for penalty in self.cat_penalties[0] +
                                 self.cat_penalties[1] +
                                 self.cat_penalties[2])
              
        
    def info(self):
        print('---------------------------------------------')
        print(self.name)
        for r in self.relation_types:
            print(f'relation: {r.name}, penalty: {r.get_penalty_norm()}')
        print('---------------------------------------------')
        
    def get_other_vessel(self, v : ActorVariable):
        if self.vessel1.id == v.id:
            return self.vessel2
        if self.vessel2.id == v.id:
            return self.vessel1
        raise Exception('Vessel is not part of the relation')
    
    def get_collision_points(self, time_limit=np.inf) -> List[np.ndarray]:
        # Relative position and velocity
        v_21 = self.vessel2.v - self.vessel1.v

        # Coefficients for the quadratic equation
        a = np.dot(v_21, v_21)
        b = 2 * np.dot(self.p12, v_21)
        c = np.dot(self.p12, self.p12) - self.safety_dist**2

        # Calculate discriminant
        discriminant = b**2 - 4*a*c

        collision_points = []

        # Check for real solutions (collision possible)
        if discriminant >= 0:
            sqrt_discriminant = np.sqrt(discriminant)

            # Find times of collision
            t1 = (-b + sqrt_discriminant) / (2 * a)
            t2 = (-b - sqrt_discriminant) / (2 * a)

            # Check if times are within the time limit and positive
            for t in [t1, t2]:
                if 0 <= t <= time_limit:
                    # Compute the collision points
                    collision_point_vessel1 = self.vessel1.p + self.vessel1.v * t
                    collision_point_vessel2 = self.vessel2.p + self.vessel2.v * t
                    collision_points.append(collision_point_vessel1)
                    collision_points.append(collision_point_vessel2)
        
        # Return the list of collision points as standard list of np.ndarray
        return collision_points


class RelationConstrTerm():
    def __init__(self) -> None:
        self.relations :  List[RelationConstr] = []
        
    def append(self, rel : RelationConstr):
        self.relations.append(rel)
        
    def update(self, assignments : Assignments):
        [rel.update(assignments) for rel in self.relations]
        self.calc_penalties()
        
    def calc_penalties(self):
        self.category_penalties = [0.0, 0.0, 0.0]
        for rel in self.relations:
            self.category_penalties[0] += sum(rel.cat_penalties[0])
            self.category_penalties[1] += sum(rel.cat_penalties[1])
            self.category_penalties[2] += sum(rel.cat_penalties[2])
        self.penalties_sum = self.category_penalties[0] + self.category_penalties[1] + self.category_penalties[2]
        
    def __repr__(self) -> str:
        return ', '.join([relation.__repr__() for relation in self.relations])
        
        