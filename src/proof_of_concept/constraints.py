import numpy as np

class COLREG():
    HEAD_ON = 'Head On'
    CROSSING_FROM_PORT = 'Crossing From Port'
    CROSSING_FROM_STARBOARD = 'Crossing From Starboard'
    OVERTAKING = 'Overtaking'
    NONE = 'None'
    

class Constraints():
    
    r1 = 30.0
    r2 = 100.0
    r = r1 + r2
    pi = np.pi
    head_on_angle = np.radians(10.0)
    overtake_angle =np.radians(120.0)
    crossing_angle = np.radians(80)
    visibility_range = 1852.001 # 6 neutical miles in metres

    speed_min = 5.0 * 0.5144447 # 5 knots in metres per second
    speed_max = 40.0 * 0.5144447
    point_min = 0.0
    point_max = 2000.0
    velocity_min = -speed_max
    velocity_max = speed_max
    
    boundaries = [(point_min, point_max), (point_min, point_max),
                    (velocity_min, velocity_max), (velocity_min, velocity_max)]

    def norm(self, x, y):
        return np.sqrt(x**2 + y**2)

    def dot(self, v1_x, v1_y, v2_x, v2_y):
        return v1_x * v2_x + v1_y * v2_y 

    def angle(self, dot, norm1, norm2): # [0, pi]
        return np.arccos((dot / norm1) / norm2)

    def interval_penalty(self, value, minimum, maximum):
        if value < minimum:
            return minimum - value
        elif value > maximum:
            return value - maximum
        else:
            return 0
    
    def __init__(self, p1_x, p1_y, p2_x, p2_y, v1_x, v1_y, v2_x, v2_y, r1, r2, verbose, colreg) -> None:
        self.colreg = colreg
        self.r1 = r1
        self.r2 = r2
        self.r = r1 + r2
        # Calculate relative position and velocity
        p12_x = p2_x - p1_x
        p12_y = p2_y - p1_y
        p21_x = p1_x - p2_x
        p21_y = p1_y - p2_y
        v12_x = v1_x - v2_x
        v12_y = v1_y - v2_y
        
        perp_p12_x = -p12_y
        perp_p12_y = p12_x
        
        # Define the norm of the relative position (distance(p1 p2))
        dist_p12 = self.norm(p12_x, p12_y)

        # Define the norm of v1 and v2
        norm_v1 = self.norm(v1_x, v1_y)
        norm_v2 = self.norm(v2_x, v2_y)

        # Define the dot product of the velocities and the relative position
        dot_product_p12_v1  = self.dot(p12_x, p12_y, v1_x, v1_y)
        dot_product_p21_v2  = self.dot(p21_x, p21_y, v2_x, v2_y)
        
        # For crossing from port calculation
        dot_product_perp_p12_v2  = self.dot(perp_p12_x, perp_p12_y, v2_x, v2_y)
        
        # For heading calculation
        dot_product_p12_v2  = self.dot(p12_x, p12_y, v2_x, v2_y)


        # Define angles between vectors
        angle_p12_v1 = self.angle(dot_product_p12_v1, dist_p12, norm_v1)
        self.angle_p12_v1 = angle_p12_v1
        angle_p21_v2 = self.angle(dot_product_p21_v2, dist_p12, norm_v2)
        angle_p12_v2 = self.angle(dot_product_p12_v2, dist_p12, norm_v2)
        self.angle_p12_v2 = angle_p12_v2

        angle_perp_p12_v2 = self.angle(dot_product_perp_p12_v2, dist_p12, norm_v2)

        # Define angle of half cone
        if self.r > dist_p12:
            self.penalties = [1e6, 1, 1, 1, 1, 1]
            return
        
        angle_half_cone = abs(np.arcsin(self.r / (dist_p12))) # [0, pi/2]

        # Define norm of v12
        norm_v12 = self.norm(v12_x, v12_y)
        
        # Define the dot product of the relative velocity and the relative position
        dot_product_v12_p12 = self.dot(v12_x, v12_y, p12_x, p12_y)
        
        # angle between the relative velocity and the relative position vector
        angle_v12_p12 = self.angle(dot_product_v12_p12, norm_v12, dist_p12)
        
        # Visibility constraint penalty
        constraint_vis = abs(dist_p12 - self.visibility_range) * 1e4
        
        # Define speed limit penalties
        constraint_v1_norm = self.interval_penalty(norm_v1, self.speed_min, self.speed_max)    
        constraint_v2_norm = self.interval_penalty(norm_v2, self.speed_min, self.speed_max)
        
        # Define VO constraint penalty
        constraint_VO = 0 if angle_v12_p12 < angle_half_cone else abs(angle_v12_p12 - angle_half_cone) * 1e3
        constraint_None_VO = 0 if angle_v12_p12 > angle_half_cone else abs(angle_v12_p12 - angle_half_cone) * 1e3
        
        # Define head-on constraint penalties
        constraint_head_on_v1 = 0 if angle_p12_v1 < self.head_on_angle / 2 else (angle_p12_v1 - self.head_on_angle / 2) * 1e3 
        constraint_head_on_v2 = 0 if angle_p21_v2 < self.head_on_angle / 2 else (angle_p21_v2 - self.head_on_angle / 2) * 1e3
        
        # Define p1 overtaking constraint
        constraint_overtaking_v1 = 0 if angle_p12_v1 < self.overtake_angle / 2 else (angle_p12_v1 - self.overtake_angle / 2) * 1e3
        constraint_overtaking_v2 = abs(angle_p12_v2) * 1e3
        
        # Define p1 crossing constraints
        constraint_crossing_v1 = 0 if angle_p12_v1 < self.crossing_angle / 2 else (angle_p12_v1 - self.crossing_angle / 2) * 1e3
        constraint_from_port_v2 = abs(angle_perp_p12_v2) * 1e3
        constraint_from_starboard_v2 = abs(angle_perp_p12_v2 - self.pi) * 1e3
        
        
        if verbose:
            print(f'Colreg situation: {colreg}\n')
            print(f'visibility distance from {self.visibility_range}: {abs(dist_p12 - self.visibility_range)}, penalty: {constraint_vis}')
            print(f'v1 length distance from bounds: {constraint_v1_norm}.')
            print(f'v2 length distance from bounds: {constraint_v2_norm}.')
            print(f'angular distance from VO cone: {angle_v12_p12 - angle_half_cone}, penalty: {constraint_VO}')
            if colreg is not COLREG.NONE:
                if colreg is COLREG.HEAD_ON:
                    print(f'angular distance from head on angle for v1: {angle_p12_v1 - self.head_on_angle / 2}, penalty: {constraint_head_on_v1}')
                    print(f'angular distance from head on angle for v2: {angle_p21_v2 - self.head_on_angle / 2}, penalty: {constraint_head_on_v2}')
                elif colreg is COLREG.OVERTAKING:
                    print(f'angular distance from overtaking angle for v1: {angle_p12_v1 - self.overtake_angle / 2}, penalty: {constraint_overtaking_v1}')
                    print(f'angular distance from overtaking angle for v2 (from 0): {angle_p12_v2}, penalty: {constraint_overtaking_v2}')
                else:
                    if colreg is COLREG.CROSSING_FROM_PORT:
                        print(f'angular distance from crossing from port angle for v2 (from 0): {angle_perp_p12_v2}, penalty: {constraint_from_port_v2}')
                    elif colreg is COLREG.CROSSING_FROM_STARBOARD:
                        print(f'angular distance from crossing from starboard angle for v2 (from 0): {angle_perp_p12_v2}, penalty: {constraint_from_starboard_v2}')
                    print(f'angular distance from crossing from port angle for v1: {angle_p12_v1 - self.crossing_angle / 2}, penalty: {constraint_crossing_v1}')
                
            
        penalties = [constraint_vis, constraint_v1_norm, constraint_v2_norm]            
        if colreg is not COLREG.NONE:
            penalties += [constraint_VO]
            if colreg is COLREG.HEAD_ON:
                penalties += [constraint_head_on_v1, constraint_head_on_v2]
            elif colreg is COLREG.OVERTAKING:
                penalties += [constraint_overtaking_v1, constraint_overtaking_v2]
            elif colreg is COLREG.CROSSING_FROM_PORT:
                penalties += [constraint_crossing_v1, constraint_from_port_v2]
            elif colreg is COLREG.CROSSING_FROM_STARBOARD:
                penalties += [constraint_crossing_v1, constraint_from_starboard_v2]
        else:
            penalties += [constraint_None_VO, 0, 0]
        
        self.penalties=penalties