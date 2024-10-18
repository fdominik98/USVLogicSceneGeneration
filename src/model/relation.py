import copy
import numpy as np
from typing import List
from model.environment.usv_config import EPSILON, o2VisibilityByo1, N_MILE_TO_M_CONVERSION
from model.vessel import OS, Vessel, VesselDesc
from model.relation_types import AtVis, CrossingBear, HeadOnBear, InVis, MayCollide, OutVis, OvertakingBear, RelationType


class RelationDesc():
    def __init__(self, vd1 : VesselDesc, relation_types : List[RelationType], vd2 : VesselDesc) -> None:
        self.relation_types = sorted(relation_types, key=lambda x: (str(type(x)), x.negated) )
        if self.all_bidir():
            self.vd1 = min([vd1, vd2], key=lambda x: x.id)
            self.vd2 = max([vd1, vd2], key=lambda x: x.id)
        else:
            self.vd1 = vd1
            self.vd2 = vd2
        
    def __repr__(self) -> str:
        return f'{self.vd1.id}-({", ".join([r.name for r in self.relation_types])})->{self.vd2.id}'
    
    def all_bidir(self):
        return all(rel.is_bidir() for rel in self.relation_types)
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RelationDesc):
            return False

        if not self.all_bidir():
            if not (self.vd1 == value.vd1 and self.vd2 == value.vd2):
                return False
        else:
            if not ((self.vd1 == value.vd1 and self.vd2 == value.vd2) or (self.vd1 == value.vd2 and self.vd2 == value.vd1)):
                return False

        if len(self.relation_types) != len(value.relation_types):
            return False
        for rel1, rel2 in zip(self.relation_types, value.relation_types):
            if type(rel1) != type(rel2) or rel1.negated != rel2.negated:
                return False

        return True
    
    def __hash__(self):
        # Combine attributes into a tuple for a unique hash
        return hash((self.vd1, self.vd2) + tuple([(type(rel), rel.negated) for rel in self.relation_types]) + ('desc',))
        
        
class RelationDescClause():
    def __init__(self, relation_descs : List[RelationDesc]) -> None:
        self.relation_descs = sorted(set(relation_descs), key=lambda x: hash(x))
        
    def append(self, rel_desc : RelationDesc):
        if rel_desc in self.relation_descs:
            return
        self.relation_descs.append(rel_desc)
        self.sort()
        
    def sort(self):
        self.relation_descs = sorted(self.relation_descs, key=lambda x: hash(x))
        
    def __repr__(self) -> str:
        return ', '.join([relation_desc.__repr__() for relation_desc in self.relation_descs])
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RelationDescClause):
            return False

        if len(self.relation_descs) != len(value.relation_descs):
            return False
        for desc1, desc2 in zip(self.relation_descs, value.relation_descs):
            if desc1 != desc2:
                return False

        return True
    
    def get_asymmetric_clause(self):
        self_copy = copy.deepcopy(self)
        for rel_desc in self_copy.relation_descs:
            rel_desc.vd1.id = 0 if isinstance(rel_desc.vd1, OS) else 1
            rel_desc.vd2.id = 0 if isinstance(rel_desc.vd2, OS) else 1
        self_copy.sort()
        return self_copy
    
    def remove_non_ego_ralations(self):
        self.relation_descs = [x for x in self.relation_descs if x.vd1.is_OS() or x.vd2.is_OS()]
        self.sort()
    
    def __hash__(self):
        # Combine attributes into a tuple for a unique hash
        return hash(tuple([desc for desc in self.relation_descs]) + ('desc',))
        
        

class Relation():
    def __init__(self, vessel1 : Vessel, relation_types : List[RelationType], vessel2 : Vessel) -> None:
        self.vessel1 = vessel1
        self.vessel2 = vessel2
        self.short_name = f'{self.vessel1.id} -> {self.vessel2.id}'
        self.relation_types : List[RelationType] = []
        self.collision_relations : List[RelationType] = []
        self.visibility_relations : List[RelationType] = []
        self.bearing_relations : List[RelationType] = []
        
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
        self.do_update()
        
    def has_os(self)-> bool:
        return self.vessel1.is_OS() or self.vessel2.is_OS()
    
    def has_collision(self) -> bool:
        for rel in self.collision_relations:
            if isinstance(rel, MayCollide) and not rel.negated:
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
           
    def update(self):
        self.do_update()
        
    def do_update(self):
        self.safety_dist = self.vessel1.r + self.vessel2.r  
        self.p12 = self.vessel2.p - self.vessel1.p
        self.p21 = self.vessel1.p - self.vessel2.p
        self.v12 = self.vessel1.v - self.vessel2.v
        
        # Define the norm of the relative position (distance(p1 p2))
        self.o_distance = max(np.linalg.norm(self.p12), EPSILON)   
        
        self.cos_p21_v2_theta = np.clip(np.dot(self.p21, self.vessel2.v) / self.o_distance / self.vessel2.speed, -1, 1)
        self.angle_p21_v2 = np.arccos(self.cos_p21_v2_theta)        
        self.cos_p12_v1_theta = np.clip(np.dot(self.p12, self.vessel1.v) / self.o_distance / self.vessel1.speed, -1, 1)
        self.angle_p12_v1 = np.arccos(self.cos_p12_v1_theta)
        
        self.vis_distance = min(o2VisibilityByo1(self.angle_p12_v1, self.vessel1.l),
                           o2VisibilityByo1(self.angle_p21_v2, self.vessel2.l)) *  N_MILE_TO_M_CONVERSION
        # angle between the relative velocity and the relative position vector
        
        self.v12_norm_stable = max(np.linalg.norm(self.v12), EPSILON)
        self.dot_p12_v12 = np.dot(self.p12, self.v12)
        #self.cos_p12_v12_theta = np.clip(self.dot_p12_v12 / self.o_distance / self.v12_norm_stable, -1, 1)
        #self.angle_v12_p12 = np.arccos(self.cos_p12_v12_theta)
        
        self.cos_p12_v12_theta = np.clip(self.dot_p12_v12 / self.o_distance / self.v12_norm_stable, -1, 1)
        self.angle_v12_p12 = np.arccos(self.cos_p12_v12_theta)
        
        self.sin_half_cone_theta = np.clip(self.safety_dist / self.o_distance, -1, 1)
        self.angle_half_cone = abs(np.arcsin(self.sin_half_cone_theta)) # [0, pi/2] 
        
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


class RelationClause():
    def __init__(self) -> None:
        self.relations :  List[Relation] = []
        self.update()
        
    def append(self, rel : Relation):
        self.relations.append(rel)
        
    def update(self):
        [rel.update() for rel in self.relations]
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
        
class RelationDisj(Relation):
    def __init__(self, relations : List[Relation]) -> None:
        self.relations = relations
        Relation.__init__(self, self.relations[0].vessel1, self.relations[0].relation_types, self.relations[0].vessel2)
        
        
    def update(self):
        min_sum_penalties = np.inf
        main_relation = self.relations[0]
        for rel in self.relations:
            Relation.__init__(self, rel.vessel1, rel.relation_types, rel.vessel2)
            
            if self.penalties_sum < min_sum_penalties:
                min_sum_penalties = self.penalties_sum
                main_relation = rel
        Relation.__init__(self, main_relation.vessel1, main_relation.relation_types, main_relation.vessel2)
        