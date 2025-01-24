import numpy as np

EPSILON=1e-10

param allowCollisions = True

BOW_ANGLE = np.radians(10.0)
STERN_ANGLE = np.radians(135)
BEAM_ANGLE = np.radians(107.5)
MASTHEAD_LIGHT_ANGLE = np.pi * 2 - STERN_ANGLE

KNOT_TO_MS_CONVERSION = 0.5144447 # 1 knot in metres per second
N_MILE_TO_M_CONVERSION = 1852.001 # 1 nautical miles in metres

DIST_DRIFT = 50.0

MAX_COORD = 2 * 6.5 * N_MILE_TO_M_CONVERSION # 24076.013 m
MAX_SPEED_IN_MS = 30 * KNOT_TO_MS_CONVERSION
MIN_SPEED_IN_MS = 2 * KNOT_TO_MS_CONVERSION

MIN_HEADING = -np.pi
MAX_HEADING = np.pi

def o2VisibilityByo1(o2RelativeBearingToo1 : float, o2_length):
    if o2RelativeBearingToo1 >= MASTHEAD_LIGHT_ANGLE / 2:
        if o2_length < 12:
            return 2
        elif o2_length < 20:
            return 2
        elif o2_length < 50:
            return 2
        else:
            return 3
    else:
        if o2_length < 12:
            return 2
        elif o2_length < 20:
            return 3
        elif o2_length < 50:
            return 5
        else:
            return 6

def calculate_heading(vx, vy):
    heading_radians = np.arctan2(vy, vx)
    return heading_radians

# class Sea(Object):
#     width: MAX_COORD - EPSILON
#     length: MAX_COORD - EPSILON
#     height: 0.01
#     position: (MAX_COORD/2, MAX_COORD/2, 0)
#     color: [150/255,220/255,250/255]

class Ship(Object):
    id : int
    is_vessel = True
    length : Range(10,100)
    color : [150/255,0/255,0/255]
    velocity : Range(-MAX_SPEED_IN_MS + 5,MAX_SPEED_IN_MS + 5)@Range(-MAX_SPEED_IN_MS + 5,MAX_SPEED_IN_MS + 5)
    max_speed : MAX_SPEED_IN_MS
    is_os : False

    def set_geometry(self):
        self.l = self.length
        self.r = self.l * 4
        self.p = self.position
        self.v = self.velocity
        self.sp = np.linalg.norm(self.v)
        self.h = calculate_heading(self.v[0], self.v[1])

    def sp_constraint(self) -> bool:
        return self.sp > MIN_SPEED_IN_MS and self.sp < MAX_SPEED_IN_MS

    def h_constraints(self) -> bool:
        return self.h > MIN_HEADING and self.h < MAX_HEADING

class OwnShip(Ship):
    length : 30
    is_os : True


class GeoProps(Object):
    is_vessel = False
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
        
        self.vis_distance = min(o2VisibilityByo1(self.angle_p12_v1, self.val1.l),
                           o2VisibilityByo1(self.angle_p21_v2, self.val2.l)) *  N_MILE_TO_M_CONVERSION
        # angle between the relative velocity and the relative position vector
        
        self.v12_norm_stable = max(np.linalg.norm(self.v12), EPSILON)
        self.dot_p12_v12 = np.dot(self.p12, self.v12)
        #self.cos_p12_v12_theta = np.clip(self.dot_p12_v12 / self.o_distance / self.v12_norm_stable, -1, 1)
        #self.angle_v12_p12 = np.arccos(self.cos_p12_v12_theta)
        
        self.tcpa = self.dot_p12_v12 / self.v12_norm_stable**2
        self.dcpa = float(np.linalg.norm(self.p21 + self.v12 * max(0, self.tcpa)))

    

    def check_constraints(self) -> bool:
        self.calculate_props()
        return (self.dcpa > 0 and 
        self.dcpa < self.safety_dist and 
        self.o_distance > self.vis_distance - DIST_DRIFT and 
        self.o_distance < self.vis_distance + DIST_DRIFT and
        self.val1.sp_constraint() and
        self.val2.sp_constraint() and 
        self.val1.h_constraints() and
        self.val2.h_constraints())


workspace = Workspace(RectangularRegion(MAX_COORD/2@MAX_COORD/2, 0, MAX_COORD, MAX_COORD))

sea = workspace

ego = new OwnShip on sea, with id 0
ship2 = new Ship on sea, with id 1

props = new GeoProps on sea, with val1 ego, with val2 ship2

# Add both ships to the scene
require props.check_constraints()


