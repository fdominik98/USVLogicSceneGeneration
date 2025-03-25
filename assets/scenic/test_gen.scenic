import numpy as np

BOW_ANGLE = np.radians(10.0)
STERN_ANGLE = np.radians(135)
BEAM_ANGLE = np.radians(112.5)
MASTHEAD_LIGHT_ANGLE = 2 * BEAM_ANGLE
BEAM_ROTATION_ANGLE = BEAM_ANGLE / 2

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

MIN_OBSTACLE_RADIUS = 10
MAX_OBSTACLE_RADIUS = 400

ONE_HOUR_IN_SEC = 60 * 60
TWO_N_MILE = 2 * N_MILE_TO_M_CONVERSION

def vessel_radius(length : float) -> float:
    return length * 4

def calculate_heading(vx : float, vy : float):
    heading_radians = np.arctan2(vy, vx)
    return heading_radians

def compute_angle(vec1, vec2, norm1, norm2):
    """Compute angle between two vectors."""
    cos_theta = np.clip(np.dot(vec1, vec2) / (norm1 * norm2), -1, 1)
    return np.arccos(cos_theta)
        

VISIBILITY_DIST_2 = 2 * N_MILE_TO_M_CONVERSION
VISIBILITY_DIST_3 = 3 * N_MILE_TO_M_CONVERSION
VISIBILITY_DIST_5 = 5 * N_MILE_TO_M_CONVERSION
VISIBILITY_DIST_6 = 6 * N_MILE_TO_M_CONVERSION

def o2VisibilityByo1(o1_sees_o2_stern : bool, o2_length : float) -> float:
    if o1_sees_o2_stern:
        if o2_length < 12:
            return VISIBILITY_DIST_2
        elif o2_length < 20:
            return VISIBILITY_DIST_2
        elif o2_length < 50:
            return VISIBILITY_DIST_2
        else:
            return VISIBILITY_DIST_3        
    else:
        if o2_length < 12:
            return VISIBILITY_DIST_2
        elif o2_length < 20:
            return VISIBILITY_DIST_3
        elif o2_length < 50:
            return VISIBILITY_DIST_5
        else:
            return VISIBILITY_DIST_6
        

# FOR FUTURE WORK
# Table 1: Approximated minimum spacing for Coldwell's domain if ownship's length and beam are L1 and B1, and target's length and beam are L2 and B2, respectively.

# Encounter/Safety Condition                      | Own Domain Not Violated | Target's Domain Not Violated | Neither Domain is Violated | Domains Not Overlapping
# ---------------------------------------------------------------------------------------------------------------------------
# Head-on (port to a target)                      | 1.75L1 - 0.5B1          | 1.75L2 - 0.5B2              | 1.75L2 - 0.5B2            | 1.75L1 - 0.5B1 + 1.75L2 - 0.5B2
# Head-on (starboard to a target)                 | 3.25L1 - 0.5B1          | 3.25L2 - 0.5B2              | 3.25L2 - 0.5B2            | 3.25L1 - 0.5B1 + 3.25L2 - 0.5B2
# Crossing ahead of a target on starboard         | 3.25L1 - 0.5B1          | 6.1L2 - 0.5L2               | 6.1L2 - 0.5L2             | 3.25L1 - 0.5B1 + 6.1L2 - 0.5L2
# Crossing astern of a target from starboard      | 1.75L1 - 0.5B1          | 3.9L2 - 0.5L2               | 3.9L2 - 0.5L2             | 1.75L1 - 0.5B1 + 3.9L2 - 0.5L2
# Crossing ahead of a target on port              | 1.75L1 - 0.5B1          | 6.1L2 - 0.5L2               | 6.1L2 - 0.5L2             | 1.75L1 - 0.5B1 + 6.1L2 - 0.5L2
# Crossing astern of a target from port           | 3.25L1 - 0.5B1          | 3.9L2 - 0.5L2               | 3.9L2 - 0.5L2             | 3.25L1 - 0.5B1 + 3.9L2 - 0.5L2
# Overtaking (port to a target or starboard)      | 1.75L1 - 0.5B1          | 1.75L2 - 0.5B2              | 1.75L2 - 0.5B2            | 1.75L1 - 0.5B1 + 1.75L2 - 0.5B2


param allowCollisions = True

class GenObject(Object):
    is_actor : False
    allowCollisions : True

    def set_geometry(self):
        pass

class Actor(GenObject):
    id : int
    length : 1
    is_vessel : False
    is_actor : True

    def sp_constraint(self) -> bool:
        return True

    def h_constraints(self) -> bool:
        return True

class Obstacle(Actor):
    area_radius : float

    def set_geometry(self):
        self.r = self.area_radius
        self.p = self.position

class Vessel(Actor):
    is_vessel : True
    is_os : False
    max_speed : MAX_SPEED_IN_MS

    def set_geometry(self):
        self.l = self.length
        self.r = vessel_radius(self.l)
        self.p = self.position
        self.v = self.velocity
        self.sp = np.linalg.norm(self.v)
        self.h = calculate_heading(self.v[0], self.v[1])
        self.v_norm = self.v / self.sp
        self.v_norm_perp = np.array([self.v_norm[1], -self.v_norm[0]])

    def sp_constraint(self) -> bool:
        return self.sp > MIN_SPEED_IN_MS and self.sp < MAX_SPEED_IN_MS

    def h_constraints(self) -> bool:
        return self.h > MIN_HEADING and self.h < MAX_HEADING

class OwnShip(Vessel):
    length : EGO_LENGTH
    beam : EGO_BEAM
    is_os : True


class GeometricProperties(GenObject):
    val1 : Actor
    val2 : Vessel
    def set_geometry(self):
        self.val1.set_geometry()
        self.val2.set_geometry()
        self.safety_dist = max(self.val1.r, self.val2.r)

        self.p12 = self.val2.p - self.val1.p
        self.p21 = self.val1.p - self.val2.p  # Avoid redundant calculations

        # Compute norm of relative position vector (distance)
        self.o_distance = float(max(np.linalg.norm(self.p12), EPSILON))

        # Compute visibility angles
        self.angle_p21_v2 = compute_angle(self.p21, self.val2.v, self.o_distance, self.val2.sp)
        
        self.sin_half_cone_p21_theta = np.clip(self.val1.r / self.o_distance, -1, 1)
        self.angle_half_cone_p21 = abs(np.arcsin(self.sin_half_cone_p21_theta))

        self.dcpa = 0.0
        self.tcpa = 0.0
        self.vis_distance = 0.0

    def check_sp_and_h_constraints(self) -> bool:
        return (self.val1.sp_constraint() and
                self.val2.sp_constraint() and 
                self.val1.h_constraints() and
                self.val2.h_constraints())

    def check_at_vis_may_collide(self):
        self.set_geometry()
        collision_pred = self.dcpa > 0 and self.dcpa < self.safety_dist
        distance_pred = (self.o_distance > self.vis_distance - DIST_DRIFT and self.o_distance < self.vis_distance + DIST_DRIFT)
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

    def check_out_vis_or_may_not_collide(self):
        self.set_geometry()
        pred = ((self.dcpa > self.safety_dist or 
            self.o_distance > self.vis_distance + DIST_DRIFT) and
            self.check_sp_and_h_constraints())
        if not pred:
            print('NoCollideOutVisProps violation')
        return pred

class ObstacleToVesselProperties(GeometricProperties):
    def set_geometry(self):
        super().set_geometry()
        self.tcpa = np.dot(self.p21, self.val2.v_norm)
        self.dcpa = np.linalg.norm(self.p21 - self.tcpa * self.val2.v_norm)
        self.vis_distance = o2VisibilityByo1(True, self.val1.r)

class VesselToVesselProperties(GeometricProperties):
    def set_geometry(self):
        super().set_geometry()
        self.v12 = self.val1.v - self.val2.v
        self.v12_norm_stable = max(np.linalg.norm(self.v12), EPSILON)

        # Compute angles
        self.angle_p12_v1 = compute_angle(self.p12, self.val1.v, self.o_distance, self.val1.sp)

        # Compute visibility distance
        self.vis_distance = min(
            o2VisibilityByo1(self.angle_p21_v2 >= MASTHEAD_LIGHT_ANGLE / 2, self.val2.l),
            o2VisibilityByo1(self.angle_p12_v1 >= MASTHEAD_LIGHT_ANGLE / 2, self.val1.l)
        )

        # Compute time and distance to closest approach
        self.tcpa = np.dot(self.p12, self.v12) / self.v12_norm_stable**2
        self.dcpa = float(np.linalg.norm(self.p21 + self.v12 * max(0, self.tcpa)))

def create_scenario(os_id, ts_ids, obst_ids, length_map, radius_map, vis_distance_map, bearing_map):
    ego = new OwnShip with id os_id, at (MAX_COORD/2, MAX_COORD/2), with velocity (0, Range(MIN_SPEED_IN_MS, MAX_SPEED_IN_MS)), facing toward (MAX_COORD/2, MAX_COORD)
    os_radius = radius_map[os_id]

    region_2 = CircularRegion(ego.position, VISIBILITY_DIST_2 + DIST_DRIFT - EPSILON).difference(CircularRegion(ego.position, VISIBILITY_DIST_2 - DIST_DRIFT + EPSILON))
    region_3 = CircularRegion(ego.position, VISIBILITY_DIST_3 + DIST_DRIFT - EPSILON).difference(CircularRegion(ego.position, VISIBILITY_DIST_3 - DIST_DRIFT + EPSILON))
    region_5 = CircularRegion(ego.position, VISIBILITY_DIST_5 + DIST_DRIFT - EPSILON).difference(CircularRegion(ego.position, VISIBILITY_DIST_5 - DIST_DRIFT + EPSILON))
    region_6 = CircularRegion(ego.position, VISIBILITY_DIST_6 + DIST_DRIFT - EPSILON).difference(CircularRegion(ego.position, VISIBILITY_DIST_6 - DIST_DRIFT + EPSILON))
    distance_region = region_2.union(region_3).union(region_5).union(region_6)
    distance = VISIBILITY_DIST_2

    def add_ts(ts_id, distance_region, distance):
        visibility_dist = vis_distance_map.get((0, ts_id), None)
        ts_length = length_map[ts_id]
        ts_radius = radius_map[ts_id]
        heading_ego_to_ts, bearing_angle_ego_to_ts, heading_ts_to_ego, bearing_angle_ts_to_ego = bearing_map.get((0, ts_id), (0, 2*np.pi, 0, 2*np.pi))
        
        if visibility_dist is not None:
            distance_region = CircularRegion(ego.position, visibility_dist + DIST_DRIFT - EPSILON).difference(CircularRegion(ego.position, visibility_dist - DIST_DRIFT + EPSILON))
            distance = visibility_dist

        bearing_region_ego_to_ts = SectorRegion(ego.position, MAX_DISTANCE*3, heading_ego_to_ts + ego.heading, bearing_angle_ego_to_ts - EPSILON)
        
        ts_point_region = distance_region.intersect(bearing_region_ego_to_ts)
        ts_point = new Point in ts_point_region

        speed_region = CircularRegion(ts_point.position, MAX_SPEED_IN_MS - EPSILON).difference(CircularRegion(ts_point.position, MIN_SPEED_IN_MS + EPSILON))
        p21 = new GenObject facing toward ego.position - ts_point.position
        bearing_region_ts_to_ego = SectorRegion(ts_point.position, MAX_DISTANCE*3, heading_ts_to_ego + p21.heading, bearing_angle_ts_to_ego - EPSILON)
        
        sin_half_cone_theta = np.clip(max(ts_radius, os_radius) / distance, -1, 1)
        angle_half_cone = abs(np.arcsin(sin_half_cone_theta))
        voc_region = SectorRegion(ts_point.position + ego.velocity, MAX_DISTANCE*3, p21.heading, 2 * angle_half_cone)

        ts_velocity_region = speed_region.intersect(voc_region).intersect(bearing_region_ts_to_ego)

        velocity_point = new Point in ts_velocity_region
        ts = new Vessel with id ts_id, at ts_point.position, with velocity velocity_point.position-ts_point.position, with length ts_length
        prop = new VesselToVesselProperties with val1 ego, with val2 ts
        return ts, prop


    def add_obst(obst_id, distance_region, distance):
        visibility_dist = vis_distance_map.get((0, obst_id), None)
        obst_radius = radius_map[obst_id]
        heading_ego_to_obst, bearing_angle_ego_to_obst, heading_obst_to_ego, bearing_angle_obst_to_ego = bearing_map.get((0, obst_id), (0, 2*np.pi, 0, 2*np.pi))
        
        if visibility_dist is not None:
            distance_region = CircularRegion(ego.position, visibility_dist + DIST_DRIFT - EPSILON).difference(CircularRegion(ego.position, visibility_dist - DIST_DRIFT + EPSILON))
            distance = visibility_dist

        bearing_region_ego_to_obst = SectorRegion(ego.position, MAX_DISTANCE*3, heading_ego_to_obst + ego.heading, bearing_angle_ego_to_obst - EPSILON)
        
        sin_half_cone_theta = np.clip(max(obst_radius, os_radius) / distance, -1, 1)
        angle_half_cone = abs(np.arcsin(sin_half_cone_theta))
        voc_region = SectorRegion(ego.position, MAX_DISTANCE*3, ego.heading, 2 * angle_half_cone)
        
        obst_point_region = distance_region.intersect(bearing_region_ego_to_obst).intersect(voc_region)
        obst_point = new Point in obst_point_region

        obst = new Obstacle with id obst_id, at obst_point.position, with area_radius obst_radius
        prop = new ObstacleToVesselProperties with val1 obst, with val2 ego
        return obst, prop

    ts_infos = [add_ts(ts_id, distance_region, distance) for ts_id in ts_ids]
    obst_infos = [add_obst(obst_id, distance_region, distance) for obst_id in obst_ids]
    return ts_infos, obst_infos
ts_infos, obst_infos = create_scenario(os_id = 0, ts_ids=[1], obst_ids=[100], length_map={0: 29.999999999900204, 1: 396.7509632730928, 100: 1}, radius_map={0: 119.99999999960082, 1: 1587.0038530923712, 100: 125.78139088744983}, vis_distance_map={}, bearing_map={})
ts1, prop1 = ts_infos.pop(0)
require prop1.check_at_vis_may_collide()
obst100, prop100 = obst_infos.pop(0)
require prop100.check_at_vis_may_collide()

prop_obst_ts0 = new ObstacleToVesselProperties with val1 obst100, with val2 ts1
require prop_obst_ts0.check_out_vis_or_may_not_collide()