import pymc as pm
import numpy as np
from proof_of_concept.constraints import Constraints

    
def norm(x, y):
    return pm.math.sqrt(x*x + y*y)

def dot(v1_x, v1_y, v2_x, v2_y):
    return v1_x * v2_x + v1_y * v2_y 

def angle(dot, norm1, norm2): # [0, pi]
    return pm.math.arccos((dot / norm1) / norm2)

def interval_penalty(value, minimum, maximum):
    return pm.math.switch((value < minimum), minimum - value,
                   pm.math.switch((value > maximum), value - maximum, 0))

# Define the model with constraints
with pm.Model() as model:
    # Define priors for each variable
    p1_x = pm.Uniform('p1_x', lower=Constraints.point_min, upper=Constraints.point_max)
    p1_y = pm.Uniform('p1_y', lower=Constraints.point_min, upper=Constraints.point_max)
    p2_x = pm.Uniform('p2_x', lower=Constraints.point_min, upper=Constraints.point_max)
    p2_y = pm.Uniform('p2_y', lower=Constraints.point_min, upper=Constraints.point_max)
    v1_x = pm.Uniform('v1_x', lower=Constraints.velocity_min, upper=Constraints.velocity_max)
    v1_y = pm.Uniform('v1_y', lower=Constraints.velocity_min, upper=Constraints.velocity_max)
    v2_x = pm.Uniform('v2_x', lower=Constraints.velocity_min, upper=Constraints.velocity_max)
    v2_y = pm.Uniform('v2_y', lower=Constraints.velocity_min, upper=Constraints.velocity_max)

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
    dist_p12 = norm(p12_x, p12_y)

    # Define the norm of v1 and v2
    norm_v1 = norm(v1_x, v1_y)
    norm_v2 = norm(v2_x, v2_y)

    # Define the dot product of the velocities and the relative position
    dot_product_p12_v1  = dot(p12_x, p12_y, v1_x, v1_y)
    dot_product_p21_v2  = dot(p21_x, p21_y, v2_x, v2_y)

    # For crossing from port calculation
    dot_product_perp_p12_v2  = dot(perp_p12_x, perp_p12_y, v2_x, v2_y)

    # For heading calculation
    dot_product_p12_v2  = dot(p12_x, p12_y, v2_x, v2_y)


    # Define angles between vectors
    angle_p12_v1 = angle(dot_product_p12_v1, dist_p12, norm_v1)
    angle_p21_v2 = angle(dot_product_p21_v2, dist_p12, norm_v2)
    angle_p12_v2 = angle(dot_product_p12_v2, dist_p12, norm_v2)

    angle_perp_p12_v2 = angle(dot_product_perp_p12_v2, dist_p12, norm_v2)

    angle_half_cone = pm.math.abs(pm.math.arcsin(Constraints.r / (dist_p12))) # [0, pi/2]

    # Define norm of v12
    norm_v12 = norm(v12_x, v12_y)

    # Define the dot product of the relative velocity and the relative position
    dot_product_v12_p12 = dot(v12_x, v12_y, p12_x, p12_y)

    # angle between the relative velocity and the relative position vector
    angle_v12_p12 = angle(dot_product_v12_p12, norm_v12, dist_p12)
    
    # Visibility constraint penalty
    constraint_vis = pm.math.abs(dist_p12 - Constraints.visibility_range) * 1e4
    
    # Define speed limit penalties
    constraint_v1_norm = interval_penalty(norm_v1, Constraints.speed_min, Constraints.speed_max)    
    constraint_v2_norm = interval_penalty(norm_v2, Constraints.speed_min, Constraints.speed_max)
    
    # Define VO constraint penalty
    constraint_VO = pm.math.switch((angle_v12_p12 < angle_half_cone), 0, pm.math.abs(angle_v12_p12 - angle_half_cone) * 1e3)
    
    # Define head-on constraint penalties
    constraint_head_on_v1 = pm.math.switch((angle_p12_v1 < Constraints.head_on_angle / 2), 0, (angle_p12_v1 - Constraints.head_on_angle / 2) * 1e3)
    constraint_head_on_v2 = pm.math.switch((angle_p21_v2 < Constraints.head_on_angle / 2), 0, (angle_p21_v2 - Constraints.head_on_angle / 2) * 1e3)
    
    # Define p1 overtaking constraint
    constraint_overtaking_v1 = pm.math.switch((angle_p12_v1 < Constraints.overtake_angle / 2), 0, (angle_p12_v1 - Constraints.overtake_angle / 2) * 1e3)
    constraint_overtaking_v2 = pm.math.abs(angle_p12_v2) * 1e3
    
    # Define p1 crossing constraints
    constraint_crossing_v1 = pm.math.switch((angle_p12_v1 < Constraints.crossing_angle / 2), 0, (angle_p12_v1 - Constraints.crossing_angle / 2) * 1e3)
    constraint_from_port_v2 = pm.math.abs(angle_perp_p12_v2) * 1e3
    constraint_from_starboard_v2 = pm.math.abs(angle_perp_p12_v2 - Constraints.pi) * 1e3

    # Define a potential to reject samples that do not satisfy the constraints
    pm.Potential('constraint_vis', -constraint_vis)
    #pm.Potential('constraint_v1_norm', -constraint_v1_norm)
    #pm.Potential('constraint_v2_norm', -constraint_v2_norm)
    #pm.Potential('constraint_VO', -constraint_VO)
    #pm.Potential('constraint_head_on_v1', -constraint_head_on_v1)
    #pm.Potential('constraint_head_on_v2', -constraint_head_on_v2)

# Sample from the model
with model:
    trace = pm.sample(1000, tune=1000, chains=2, cores=1, return_inferencedata=False)

# Extract samples
samples = trace.get_values(['p1_x', 'p1_y', 'p2_x', 'p2_y', 'v1_x', 'v1_y', 'v2_x', 'v2_y'])
print(samples)