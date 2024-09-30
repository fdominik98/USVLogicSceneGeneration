import numpy as np
from typing import List
from model.environment.usv_config import EPSILON, o2VisibilityByo1, N_MILE_TO_M_CONVERSION
from model.vessel import Vessel, VesselDesc
from model.relation_types import AtVis, CrossingBear, HeadOnBear, InVis, MayCollide, OutVis, OvertakingBear, RelationType


class RelationDesc():
    def __init__(self, vd1 : VesselDesc, relations : List[RelationType], vd2 : VesselDesc) -> None:
        self.vd1 = vd1
        self.relations = relations
        self.vd2 = vd2

class Relation():
    def __init__(self, vessel1 : Vessel, relations : List[RelationType | List[RelationType]], vessel2 : Vessel) -> None:
        self.vessel1 = vessel1
        self.vessel2 = vessel2
        self.short_name = f'{self.vessel1.id} -> {self.vessel2.id}'
        self.safety_dist = vessel1.r + vessel2.r  
        self.relations : List[RelationType] = []
        self.collision_relations : List[RelationType] = []
        self.visibility_relations : List[RelationType] = []
        self.bearing_relations : List[RelationType] = []
        for relation in relations:
            if not isinstance(relation, list):
                relation = [relation]  # Wrap in list if not already
            for r in relation:
                r.set_relation(self)
                if isinstance(r, MayCollide):
                    self.collision_relations.append(r)
                if isinstance(r, AtVis) or isinstance(r, InVis) or isinstance(r, OutVis):
                    self.visibility_relations.append(r)
                if isinstance(r, HeadOnBear) or isinstance(r, CrossingBear) or isinstance(r, OvertakingBear):
                    self.bearing_relations.append(r)
                self.relations.append(r)
            
        self.name = rf'{self.vessel1} - ({", ".join([r.name for r in self.relations])}) -> {self.vessel2}'
        self.update()
        
    def has_os(self)-> bool:
        return self.vessel1.id == 0 or self.vessel2.id == 0
    
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
        
    def update(self):
        self.p12 = self.vessel2.p - self.vessel1.p
        self.p21 = self.vessel1.p - self.vessel2.p
        self.v12 = self.vessel1.v - self.vessel2.v
        
        # Define the norm of the relative position (distance(p1 p2))
        self.o_distance = np.linalg.norm(self.p12)   
        
        self.angle_p21_v2 = np.arccos(np.dot(self.p21, self.vessel2.v) / self.o_distance / self.vessel2.speed)        
        self.angle_p12_v1 = np.arccos(np.dot(self.p12, self.vessel1.v) / self.o_distance / self.vessel1.speed)
        
        self.vis_distance = min(o2VisibilityByo1(self.angle_p12_v1, self.vessel1.l),
                           o2VisibilityByo1(self.angle_p21_v2, self.vessel2.l)) *  N_MILE_TO_M_CONVERSION
        # angle between the relative velocity and the relative position vector
        self.angle_v12_p12 = np.arccos(np.dot(self.p12, self.v12) / self.o_distance / np.linalg.norm(self.v12))
        
        stable_norm_p12 = max(self.o_distance, EPSILON)
        sin_theta = np.clip(self.safety_dist / stable_norm_p12, -1, 1)
        self.angle_half_cone = abs(np.arcsin(sin_theta)) # [0, pi/2]  
        
        
    def info(self):
        print('---------------------------------------------')
        print(self.name)
        for r in self.relations:
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

