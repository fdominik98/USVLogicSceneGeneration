import re
from dreal import (Variable, sqrt, asin, acos, CheckSatisfiability, And)
from proof_of_concept.constraints import Constraints

def norm(x, y):
    return sqrt(x*x + y*y)

def dot(v1_x, v1_y, v2_x, v2_y):
    return v1_x * v2_x + v1_y * v2_y 

def angle(dot, norm1, norm2): # [0, pi]
    return acos((dot / norm1) / norm2)

p1_x = Variable("p1_x")
p1_y = Variable("p1_y")
p2_x = Variable("p2_x")
p2_y = Variable("p2_y")
v1_x = Variable("v1_x")
v1_y = Variable("v1_y")
v2_x = Variable("v2_x")
v2_y = Variable("v2_y")
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

angle_half_cone = abs(asin(Constraints.r / (dist_p12))) # [0, pi/2]

# Define norm of v12
norm_v12 = norm(v12_x, v12_y)

# Define the dot product of the relative velocity and the relative position
dot_product_v12_p12 = dot(v12_x, v12_y, p12_x, p12_y)

# angle between the relative velocity and the relative position vector
angle_v12_p12 = angle(dot_product_v12_p12, norm_v12, dist_p12)

f_sat = And(Constraints.point_min <= p1_x, p1_x <= Constraints.point_max,
            Constraints.point_min <= p1_y, p1_y <= Constraints.point_max,
            Constraints.point_min <= p2_x, p2_x <= Constraints.point_max,
            Constraints.point_min <= p2_y, p2_y <= Constraints.point_max,
            Constraints.velocity_min <= v1_x, v1_x <= Constraints.velocity_max,
            Constraints.velocity_min <= v1_y, v1_y <= Constraints.velocity_max,
            Constraints.velocity_min <= v2_x, v2_x <= Constraints.velocity_max,
            Constraints.velocity_min <= v2_y, v2_y <= Constraints.velocity_max,
            #dist_p12 == Constraints.visibility_range,
            norm_v1 >= Constraints.speed_min, norm_v1 <= Constraints.speed_max,
            norm_v2 >= Constraints.speed_min, norm_v2 <= Constraints.speed_max,
            angle_v12_p12 < angle_half_cone,
            angle_p12_v1 < Constraints.head_on_angle / 2, angle_p21_v2 < Constraints.head_on_angle / 2, # Head on
            #angle_p12_v1 < Constraints.overtake_angle / 2, abs(angle_p12_v2) == 0, # Overtake
            #angle_p12_v1 < Constraints.crossing_angle / 2, abs(angle_perp_p12_v2) == 0, # Crossing from port
            #angle_p12_v1 < Constraints.crossing_angle / 2, abs(angle_perp_p12_v2) == Constraints.pi, # Crossing from starboard
            )

result = CheckSatisfiability(f_sat, 0.01)
print(result)

import re
import ast

def parse_box_string(box_string):
    # Remove the enclosing <Box " and ">
    box_string = box_string.strip('<Box "').strip('">')

    # Split the string into lines
    lines = box_string.split('\n')

    variables = {}

    # Regular expression to match variable names and their values
    pattern = re.compile(r'(\w+) : (.+)')

    for line in lines:
        match = pattern.match(line)
        if match:
            var_name = match.group(1)
            var_value = match.group(2)

            # Evaluate the value to get it as a list or float
            value = ast.literal_eval(var_value)
            
            if isinstance(value, list):
                # Calculate the average of the min and max
                avg_value = sum(value) / len(value)
            else:
                # Use the value directly if it's not a list
                avg_value = value

            # Store the result in the dictionary
            variables[var_name] = avg_value

    return variables

# Parse the output
variables_dict = parse_box_string(str(result))
variables_dict['r1'] = Constraints.r1
variables_dict['r2'] = Constraints.r2
variables_dict['colreg'] = Constraints.COLREG
variables_dict['r1'] = Constraints.r1
variables_dict['angle_p12_v1'] = 0
variables_dict['angle_p12_v2'] = 0

print(variables_dict)