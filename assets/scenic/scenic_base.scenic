import itertools
import sys
import os
import numpy as np

BOW_ANGLE = np.radians(10.0)
STERN_ANGLE = np.radians(135)
BEAM_ANGLE = np.radians(112.5)
MASTHEAD_LIGHT_ANGLE = 2 * BEAM_ANGLE

KNOT_TO_MS_CONVERSION = 0.5144447 # 1 knot in metres per second
N_MILE_TO_M_CONVERSION = 1852.001 # 1 nautical miles in metres

DIST_DRIFT = 50.0

# 6 nautical miles = 11112,066 meters
# 5 nautical miles = 9260,005 meters
# 4 nautical miles = 7408,004 meters
# 3 nautical miles = 5556,003 meters
# 2 nautical miles = 3704,002 meters

MIN_HEADING = -np.pi
MAX_HEADING = np.pi
MIN_COORD = 0.0
MAX_COORD = 2 * 6.5 * N_MILE_TO_M_CONVERSION # 24076.013 m
MAX_DISTANCE = MAX_COORD * np.sqrt(2) # 34048.624 m

EPSILON=1e-10

MIN_LENGTH = 10
MAX_LENGTH = 400
MIN_BEAM = 2
MAX_BEAM = 80
MIN_SPEED_IN_MS = 0.2 * KNOT_TO_MS_CONVERSION
MAX_SPEED_IN_MS = 50 * KNOT_TO_MS_CONVERSION

EGO_LENGTH = 30
EGO_BEAM = 10

ONE_HOUR_IN_SEC = 60 * 60
TWO_N_MILE = 2 * N_MILE_TO_M_CONVERSION

def vessel_radius(length : float) -> float:
    return length * 4

def calculate_heading(vx : float, vy : float):
    heading_radians = np.arctan2(vy, vx)
    return heading_radians
        
def o2VisibilityByo1(o1_sees_o2_stern : bool, o2_length : float):
    if o1_sees_o2_stern:
        if o2_length < 12:
            return 2
        elif o2_length < 20:
            return 3
        elif o2_length < 50:
            return 5
        else:
            return 6
    else:
        if o2_length < 12:
            return 2
        elif o2_length < 20:
            return 2
        elif o2_length < 50:
            return 2
        else:
            return 3   

param allowCollisions = True

class Ship(Object):
    id : int
    is_vessel = True
    color : [150/255,0/255,0/255]
    max_speed : MAX_SPEED_IN_MS
    is_os : False

    def set_geometry(self):
        self.l = self.length
        self.r = vessel_radius(self.l)
        self.p = self.position
        self.v = self.velocity
        self.sp = np.linalg.norm(self.v)
        self.h = calculate_heading(self.v[0], self.v[1])

    def sp_constraint(self) -> bool:
        return self.sp > MIN_SPEED_IN_MS and self.sp < MAX_SPEED_IN_MS

    def h_constraints(self) -> bool:
        return self.h > MIN_HEADING and self.h < MAX_HEADING

class OwnShip(Ship):
    length : EGO_LENGTH
    beam : EGO_BEAM
    is_os : True

class DummyShip(Ship):
    is_vessel = False
    allowCollisions : True

class GeoProps(Object):
    is_vessel : False
    allowCollisions : True
    val1 : Ship
    val2 : Ship
    def calculate_props(self):
        self.val1.set_geometry()
        self.val2.set_geometry()
        self.safety_dist = max(self.val1.r, self.val2.r)
        self.p12 = self.val2.p - self.val1.p
        self.p21 = self.val1.p - self.val2.p
        self.v12 = self.val1.v - self.val2.v
        
                # Define the norm of the relative position (distance(p1 p2))
        self.o_distance = float(max(np.linalg.norm(self.p12), EPSILON))
        
        self.cos_p21_v2_theta = np.clip(np.dot(self.p21, self.val2.v) / self.o_distance / self.val2.sp, -1, 1)
        self.angle_p21_v2 = np.arccos(self.cos_p21_v2_theta)        
        self.cos_p12_v1_theta = np.clip(np.dot(self.p12, self.val1.v) / self.o_distance / self.val1.sp, -1, 1)
        self.angle_p12_v1 = np.arccos(self.cos_p12_v1_theta)
        
        self.vis_distance = min(o2VisibilityByo1(self.angle_p21_v2 >= MASTHEAD_LIGHT_ANGLE / 2, self.val2.l),
                                o2VisibilityByo1(self.angle_p12_v1 >= MASTHEAD_LIGHT_ANGLE / 2, self.val1.l)) *  N_MILE_TO_M_CONVERSION
        # angle between the relative velocity and the relative position vector
        
        self.v12_norm_stable = max(np.linalg.norm(self.v12), EPSILON)
        self.dot_p12_v12 = np.dot(self.p12, self.v12)
        #self.cos_p12_v12_theta = np.clip(self.dot_p12_v12 / self.o_distance / self.v12_norm_stable, -1, 1)
        #self.angle_v12_p12 = np.arccos(self.cos_p12_v12_theta)
        
        self.tcpa = self.dot_p12_v12 / self.v12_norm_stable**2
        self.dcpa = float(np.linalg.norm(self.p21 + self.v12 * max(0, self.tcpa)))

    def check_sp_and_h_constraints(self) -> bool:
        return (self.val1.sp_constraint() and
                self.val2.sp_constraint() and 
                self.val1.h_constraints() and
                self.val2.h_constraints())

    def check_constraints(self):
        pass

class AtVisMayCollideProps(GeoProps):
    def check_constraints(self):
        self.calculate_props()
        collision_pred = self.dcpa > 0 and self.dcpa < self.safety_dist
        distance_pred = self.o_distance > self.vis_distance - DIST_DRIFT and self.o_distance < self.vis_distance + DIST_DRIFT
        sp_h_violation = self.check_sp_and_h_constraints()
        pred = collision_pred and distance_pred and sp_h_violation
        if not pred:
            print('AtVisMayCollideProps violation')
            if not collision_pred:
                print('Collision violation')
            if not distance_pred:
                print(f'Distance violation: real:{self.o_distance/N_MILE_TO_M_CONVERSION}, vis:{self.vis_distance/N_MILE_TO_M_CONVERSION} ({self.val1.id, self.val2.id})')
            if not sp_h_violation:
                print('sp, h violation')
        return pred

class NoCollideOutVisProps(GeoProps):
    def check_constraints(self):
        self.calculate_props()
        pred = ((self.dcpa > self.safety_dist or 
            self.o_distance > self.vis_distance + DIST_DRIFT) and
            self.check_sp_and_h_constraints())
        if not pred:
            print('NoCollideOutVisProps violation')
        return pred

def create_scenario(ts_num):
    ego = new OwnShip with id 0, at (MAX_COORD/2, MAX_COORD/2), with velocity (0, Range(MIN_SPEED_IN_MS, MAX_SPEED_IN_MS)), facing toward (MAX_COORD/2, MAX_COORD)
    # region_2 = CircularRegion(ego.position, 2 * N_MILE_TO_M_CONVERSION + DIST_DRIFT).difference(CircularRegion(ego.position, 2 * N_MILE_TO_M_CONVERSION - DIST_DRIFT))
    # region_3 = CircularRegion(ego.position, 3 * N_MILE_TO_M_CONVERSION + DIST_DRIFT).difference(CircularRegion(ego.position, 3 * N_MILE_TO_M_CONVERSION - DIST_DRIFT))
    # region_5 = CircularRegion(ego.position, 5 * N_MILE_TO_M_CONVERSION + DIST_DRIFT).difference(CircularRegion(ego.position, 5 * N_MILE_TO_M_CONVERSION - DIST_DRIFT))
    # region_6 = CircularRegion(ego.position, 6 * N_MILE_TO_M_CONVERSION + DIST_DRIFT).difference(CircularRegion(ego.position, 6 * N_MILE_TO_M_CONVERSION - DIST_DRIFT))
    #distance_region = region_2.union(region_3).union(region_5).union(region_6)

    # sin_half_cone_theta = np.clip(vessel_radius(MAX_LENGTH) / (2 * N_MILE_TO_M_CONVERSION - DIST_DRIFT), -1, 1)
    # angle_half_cone = abs(np.arcsin(sin_half_cone_theta))
    # sin_half_cone_theta_3 = np.clip(100*4 / (3 * N_MILE_TO_M_CONVERSION - DIST_DRIFT), -1, 1)
    # angle_half_cone_3 = abs(np.arcsin(sin_half_cone_theta))
    # sin_half_cone_theta_5 = np.clip(100*4 / (5 * N_MILE_TO_M_CONVERSION - DIST_DRIFT), -1, 1)
    # angle_half_cone_5 = abs(np.arcsin(sin_half_cone_theta))
    # sin_half_cone_theta_6 = np.clip(100*4 / (6 * N_MILE_TO_M_CONVERSION - DIST_DRIFT), -1, 1)
    # angle_half_cone_6 = abs(np.arcsin(sin_half_cone_theta))

    def add_ts(ts_id):
        visibility_dist = vis_distance_map[(0, ts_id)]
        ts_length = length_map[ts_id]
        heading_ego_to_ts, bearing_angle_ego_to_ts, heading_ts_to_ego, bearing_angle_ts_to_ego = bearing_map[(0, ts_id)]
        
        distance_region = CircularRegion(ego.position, visibility_dist + DIST_DRIFT - EPSILON).difference(CircularRegion(ego.position, visibility_dist - DIST_DRIFT + EPSILON))
        bearing_region_ego_to_ts = SectorRegion(ego.position, MAX_DISTANCE, heading_ego_to_ts + ego.heading, bearing_angle_ego_to_ts - EPSILON)
        ts_point_region = distance_region.intersect(bearing_region_ego_to_ts)

        ts_point = new Point in ts_point_region

        sin_half_cone_theta = np.clip(max(vessel_radius(ts_length), vessel_radius(ego.length)) / visibility_dist, -1, 1)
        angle_half_cone = abs(np.arcsin(sin_half_cone_theta))

        speed_region = CircularRegion(ts_point.position, MAX_SPEED_IN_MS - EPSILON).difference(CircularRegion(ts_point.position, MIN_SPEED_IN_MS + EPSILON))
        p21 = new DummyShip with id 1000, facing toward ego.position - ts_point.position
        bearing_region_ts_to_ego = SectorRegion(ts_point.position, MAX_DISTANCE, heading_ts_to_ego + p21.heading, bearing_angle_ts_to_ego - EPSILON)
        voc_region = SectorRegion(ts_point.position + ego.velocity, MAX_DISTANCE, p21.heading, 2 * angle_half_cone)
        ts_velocity_region = speed_region.intersect(voc_region).intersect(bearing_region_ts_to_ego)

        velocity_point = new Point in ts_velocity_region
        ts = new Ship with id ts_id, at ts_point.position, with velocity velocity_point.position-ts_point.position, with length ts_length
        prop = new AtVisMayCollideProps with val1 ego, with val2 ts
        return ts, prop
    return [add_ts(i+1) for i in range(ts_num)]