from model.usv_config import MAX_COORD, MIN_COORD
from visualization.colreg_plot import ColregPlot
from visualization.data_parser import DataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment
from visualization.colreg_animation import ColregAnimation
from rrt_algorithms.rrt.rrt import RRT
from rrt_algorithms.search_space.search_space import SearchSpace
from rrt_algorithms.utilities.plotting import Plot

import numpy as np

dp = DataParser()
df, _ = dp.load_files()

if df.size == 0:
    exit(0)

config = USV_ENV_DESC_LIST[df['config_name'][0]]
env = USVEnvironment(config).update(df['best_solution'][0])
ColregPlot(env)

colreg_s = list(env.colreg_situations)[0]
o1 = env.vessels[0]
o2 = env.vessels[1]

from ompl import base as ob
from ompl import geometric as og
from ompl import control as oc

def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def is_safe(state1, state2, safety_distance):
    return distance(state1, state2) >= safety_distance


class SafeMotionPlanner:
    def __init__(self, safety_distance):
        # Define the state space
        self.space = ob.RealVectorStateSpace(4)  # Two objects, each with 2D position (x, y)

        # Set bounds for the state space
        bounds = ob.RealVectorBounds(4)
        bounds.setLow(0, -10)
        bounds.setHigh(0, 10)
        bounds.setLow(1, -10)
        bounds.setHigh(1, 10)
        bounds.setLow(2, -1)
        bounds.setHigh(2, 1)
        bounds.setLow(3, -1)
        bounds.setHigh(3, 1)
        self.space.setBounds(bounds)

        # Create the space information
        self.si = ob.SpaceInformation(self.space)
        self.safety_distance = safety_distance

        # Define the state validity checker
        self.si.setStateValidityChecker(self.state_validity_checker)

    def state_validity_checker(self, state):
        state = np.array(state)
        pos1 = state[:2]
        pos2 = state[2:4]
        return is_safe(pos1, pos2, self.safety_distance)

    def plan(self, start, goal):
        # Set the start and goal states
        start_state = ob.State(self.space)
        goal_state = ob.State(self.space)
        start_state[:] = start
        goal_state[:] = goal

        # Define the problem
        problem = ob.ProblemDefinition(self.si)
        problem.setStartAndGoalStates(start_state, goal_state)

        # Define the planner
        planner = og.RRTConnect(self.si)
        planner.setProblemDefinition(problem)
        planner.setup()

        # Solve the problem
        if planner.solve(10.0):
            print("Solution found")
            path = problem.getSolutionPath()
            path.interpolate()
            return path
        else:
            print("No solution found")
            return None

# Example usage
planner = SafeMotionPlanner(safety_distance=1.0)

# Define start and goal states for two objects
start_state = [0, 0, 2, 2]  # (x1, y1, x2, y2)
goal_state = [5, 5, 7, 7]

# Plan the trajectory
path = planner.plan(start_state, goal_state)

if path:
    print("Path found")
else:
    print("No path found")