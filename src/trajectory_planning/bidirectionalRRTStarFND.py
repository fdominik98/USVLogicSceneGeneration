import random
from typing import List, Optional, Tuple
import numpy as np
from trajectory_planning.vessel_order_graph import VesselNode
from trajectory_planning.rrt_utils import Node, Obstacle, RandomPoint, TrajectoryState
from trajectory_planning.path_interpolator import PathInterpolator

DIM = 1000

show_animation = True
class RRTStarFND():
    """
    Class for RRT Planning
    """
    def __init__(self, v_node : VesselNode, start : np.ndarray, goal : np.ndarray,
                 obstacle_list : List[Obstacle], sample_area : List[Tuple[float, float]], 
                 collision_points : List[np.ndarray], interpolator : PathInterpolator,
                expand_dist=10.0, goal_sample_rate=15, max_iter=1500, scaler = 1.0, max_nodes = 1500):
        self.vessel = v_node.vessel
        self.collision_points = collision_points
        self.interpolator = interpolator
        self.start = Node(start)
        self.end = Node(goal)
        self.delta_pos_start_end = self.end.p - self.start.p
        self.start_end_distance = np.linalg.norm(self.delta_pos_start_end)
        self.sample_area = sample_area
        self.expand_dist = expand_dist
        self.goal_sample_rate = goal_sample_rate
        self.max_iter = max_iter
        self.obstacle_list : List[Obstacle] = obstacle_list
        self.current_i = 0
        self.stop = False
        self.scaler = scaler
        self.max_nodes = max_nodes
        
        if show_animation:
            from trajectory_planning.trajectory_visualizer import TrajectoryVisualizer
            self.trajectory_visualizer = TrajectoryVisualizer(DIM, scaler, sample_area)
            self.trajectory_visualizer.set_caption(v_node, interpolator)
            

    def do_plan(self) -> Optional[List[Node]]:
        while self.current_i < self.max_iter and not self.stop:
            if self.current_i % 100 == 0:
                print(self.current_i)

            rnd = self.get_random_point()
            nearest_index = self.get_nearest_list_index(rnd) # get nearest node index to random point
            new_node = self.steer(rnd, nearest_index) # generate new node from that nearest node in direction of random point

            if self.check_no_collision(new_node, self.obstacle_list): # if it does not collide

                nearest_indexes = self.find_near_nodes(new_node, 5) # find nearest nodes to newNode
                found = self.choose_parent(new_node, nearest_indexes) # from that nearest nodes find the best parent to newNode
                if not found:
                    continue
                self.node_list[self.current_i + 100] = new_node # add newNode to nodeList
                self.rewire(self.current_i + 100, new_node, nearest_indexes) # make newNode a parent of another node if necessary
                self.node_list[new_node.parent].children.add(self.current_i + 100)

                if len(self.node_list) > self.max_nodes:
                    self.prune_branches()

            if show_animation:
                if self.current_i % 25 == 0:
                    self.trajectory_visualizer.update(self.obstacle_list, self.collision_points, self.start, self.end,
                                                    self.node_list, self.get_best_last_index(), self.gen_final_course)
                if self.trajectory_visualizer.handle_user_input(self.end, self.obstacle_list, self.path_validation):
                    self.stop = True
                        
            self.current_i += 1
                        
        # generate coruse
        lastIndex = self.get_best_last_index()
        if lastIndex is None:
            return None
        path = self.gen_final_course(lastIndex)
        return path
    
    def prune_branches(self):
        leaves = [ key for key, node in self.node_list.items() if len(node.children) == 0 and len(self.node_list[node.parent].children) > 1] 
        if len(leaves) > 0:
            ind = leaves[random.randint(0, len(leaves)-1)]
            self.node_list[self.node_list[ind].parent].children.discard(ind)
            self.node_list.pop(ind)
        else:
            leaves = [ key for key, node in self.node_list.items() if len(node.children) == 0 ]
            ind = leaves[random.randint(0, len(leaves)-1)]
            self.node_list[self.node_list[ind].parent].children.discard(ind)
            self.node_list.pop(ind)
        

    def plan_trajectory(self) -> List[Node]:
        """
        plan_trajectory
        animation: flag for animation on or off
        """
        self.node_list = {0 : self.start}
        path = None
        while(path is None):
            path = self.do_plan()
            if path is None:
                if self.current_i == self.max_iter:
                    self.max_iter += 100
                    print("No solution repeating for 100 more iterations.")
        path.reverse()
        return path     

    def path_validation(self):
        lastIndex = self.get_best_last_index()
        if lastIndex is not None:
            while self.node_list[lastIndex].parent is not None:
                nodeInd = lastIndex
                lastIndex = self.node_list[lastIndex].parent
                if not self.check_no_collision_extend(self.node_list[lastIndex], self.node_list[nodeInd])[0]:
                    self.node_list[lastIndex].children.discard(nodeInd)
                    self.remove_branch(nodeInd)

    def remove_branch(self, nodeInd):
        for ix in self.node_list[nodeInd].children:
            self.remove_branch(ix)
        self.node_list.pop(nodeInd)

    def choose_parent(self, new_node : Node, nearest_indexes):
        if len(nearest_indexes) == 0:
            return False

        min_cost = np.inf
        min_cost_state = None
        min_cost_index = None
        for i in nearest_indexes:
            no_coll, dist, next_state = self.check_no_collision_extend(self.node_list[i], new_node)
            if no_coll:
                cost = self.node_list[i].distance_cost + dist
                if cost < min_cost:
                    min_cost = cost
                    min_cost_index = i
                    min_cost_state = next_state

        if min_cost_index == None:
            print("min_cost is inf")
            return False

        new_node.distance_cost = min_cost
        new_node.parent = min_cost_index
        new_node.state = min_cost_state
        return True

    def steer(self, rnd : RandomPoint, nearest_index : int):
        # expand tree
        nearest_node = self.node_list[nearest_index]
        delta_pos = rnd.p - nearest_node.p
        theta = np.arctan2(delta_pos[1], delta_pos[0])        
        new_point = nearest_node.p + np.array([np.cos(theta), np.sin(theta)]) * self.expand_dist
        new_node = Node(new_point)
        
        # # Apply the condition for adjusting theta
        # abs_theta = abs(theta)  # Work with absolute value of theta for comparison

        # if abs_theta < np.radians(30):
        #     theta = 0  # Set to 0 if below 30 degrees
        # elif abs_theta > np.radians(60):
        #     theta = np.sign(theta) * np.radians(60)  # Cap at 60 degrees with the same sign
        
        s_dist, s_fraction = Node.calc_cost(self.vessel, self.expand_dist)
        new_node.set_cost(nearest_node.distance_cost + self.expand_dist, nearest_node.time_cost + s_dist, s_fraction)
        new_node.parent = nearest_index
        return new_node

    def get_random_point(self) -> RandomPoint:
        if random.randint(0, 100) > self.goal_sample_rate:
           return RandomPoint(np.array([random.uniform(*self.sample_area[0]), random.uniform(*self.sample_area[1])]), False)
        return RandomPoint(np.array([self.end.p[0], self.end.p[1]]), True)

    def get_best_last_index(self):
        dist_to_goal_list = [(key, np.linalg.norm(self.end.p - node.p)) for key, node in self.node_list.items()]
        near_goal_indexes = [key for key, distance in dist_to_goal_list if distance <= self.expand_dist]

        if len(near_goal_indexes) == 0:
            return None

        min_cost = min([self.node_list[key].distance_cost for key in near_goal_indexes])
        for i in near_goal_indexes:
            if self.node_list[i].distance_cost == min_cost:
                return i

        return None

    def gen_final_course(self, goal_index : int) -> List[Node]:
        path = [self.end]
        while self.node_list[goal_index].parent is not None:
            node = self.node_list[goal_index]
            path.append(node)
            goal_index = node.parent
        path.append(self.start)
        return path


    def find_near_nodes(self, newNode: Node, value):
        r_squared = (self.expand_dist * value) ** 2  # Compute the squared distance threshold once

        new_p = newNode.p
        node_positions = np.array([node.p for node in self.node_list.values()])  # Extract positions
        node_keys = np.array(list(self.node_list.keys()))  # Extract node keys

        # Compute squared distances between nodes and newNode
        dist_squared = np.sum((node_positions - new_p) ** 2, axis=1)

        # Find nodes with distances less than or equal to r_squared
        nearest_indexes = node_keys[dist_squared <= r_squared]

        return nearest_indexes
    

    def rewire(self, new_node_index : int, new_node : Node, near_indexes : List[int]):
        for i in near_indexes:
            near_node = self.node_list[i]

            d = np.linalg.norm(new_node.p - near_node.p)
            new_cost = new_node.distance_cost + d

            if near_node.distance_cost > new_cost:
                no_coll, dist, next_state = self.check_no_collision_extend(new_node, near_node)
                if no_coll:
                    self.node_list[near_node.parent].children.discard(i)
                    near_node.parent = new_node_index
                    s_d, s_fraction = Node.calc_cost(self.vessel, d)
                    near_node.set_cost(new_cost, s_d + new_node.time_cost, s_fraction)
                    near_node.state = next_state
                    new_node.children.add(i)
                    
    

    def get_nearest_list_index(self, rnd: RandomPoint):
        rnd_p = rnd.p
        node_keys = list(self.node_list.keys())
        node_positions = np.array([node.p for node in self.node_list.values()])
        
        # Compute squared distances directly and lazily find the min
        dist_squared = np.sum((node_positions - rnd_p)**2, axis=1)
        
        # Get the index with the minimum distance
        min_index = node_keys[np.argmin(dist_squared)]
        
        return min_index
    

    def check_no_collision_extend(self, parent_node : Node, node : Node) -> Tuple[bool, float, Optional[TrajectoryState]]:
        next_state = TrajectoryState.START
        delta_pos = node.p - parent_node.p
        dist = float(np.linalg.norm(delta_pos))
        if parent_node.parent is not None:
             delta_pos_parent = parent_node.p - self.node_list[parent_node.parent].p
             angle_parent = self.angle_between_vectors(delta_pos_parent, delta_pos, dist)
             if not (np.radians(0) <= angle_parent <= np.radians(5) or
                     np.radians(30) <= angle_parent <= np.radians(60)):
                 return False, dist, next_state
        #     next_state = self.state_transitions(parent_node, delta_pos_parent, delta_pos, dist)
        #else:
        #     if parent_node.state != TrajectoryState.START:
        #         raise Exception('Root node must be in START state')
        #     next_state = self.state_transitions(parent_node, None, delta_pos, dist)
        # if next_state is None:
        #     return False, dist, None
        
        tmpNode = Node(np.array([parent_node.p[0], parent_node.p[1]]))
        s_d, s_fraction = Node.calc_cost(self.vessel, dist)
        s_d = s_d - np.ceil(s_fraction)
        
        for s in range(int(s_d)):
            fraction = s / s_d
            tmpNode.p = parent_node.p + delta_pos * fraction
            tmpNode.set_cost(0, parent_node.time_cost + s, 0.0)
            if not self.check_no_collision(tmpNode, self.obstacle_list):
                return False, dist, None
        return True, dist, next_state


    def check_no_collision(self, node : Node, obstacleList : List[Obstacle]):
        for obs in obstacleList:
            if not obs.check_no_collision(node):
                print(f'Hit obstacle {obs} at {node.p}')
                return False
            
        # The two trajectories will collide at the specific second
        for obs_vessel, pos in self.interpolator.get_positions_by_second(node.time_cost):
            if np.linalg.norm(node.p - pos) <= (self.vessel.r + obs_vessel.r) * 2:
                print(f'Hit trajectory of {obs_vessel} at {pos}.')
                return False
        return True  # safe
    
            
    def angle_between_vectors(self, vec1, vec2, dist2):
        # Calculate the dot product
        dot_product = np.dot(vec1, vec2)
        # Calculate the magnitudes of the vectors
        magnitude1 = np.linalg.norm(vec1)
        # Calculate the cosine of the angle
        cos_theta = dot_product / (magnitude1 * dist2)
        # Clip the cosine value to be within the valid range for arccos
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        # Calculate the angle in radians and then in degrees
        return np.arccos(cos_theta)
    
    def cross_2d(self, reference, vec1, vec2):
        # A and B are 2D vectors (numpy arrays)
        reference = reference / np.linalg.norm(reference)
        vec1 = vec1 / np.linalg.norm(vec1)
        vec2 = vec2 / np.linalg.norm(vec2)
        sub_vec = vec2 - vec1
        sub_vec = sub_vec / np.linalg.norm(sub_vec)
        return reference[0] * sub_vec[1] - reference[1] * sub_vec[0]
    
    def state_transitions(self, parent_node : Node, delta_pos_parent, delta_pos, dist_parent):
        angle_start_end = self.angle_between_vectors(self.delta_pos_start_end, delta_pos, dist_parent)
        straight_angle_pred = np.radians(0) <= angle_start_end < np.radians(5)
        if parent_node.state == TrajectoryState.START:
            arc_angle_pred = np.radians(1) <= angle_start_end <= np.radians(40)
            cross_start_end = self.cross_2d(self.delta_pos_start_end, self.delta_pos_start_end, delta_pos)
            if straight_angle_pred:
                return TrajectoryState.STAND_ON_1
            elif cross_start_end < 0 and arc_angle_pred:
                return TrajectoryState.GIVE_WAY_ARC
            return None
        
        angle_parent = self.angle_between_vectors(delta_pos_parent, delta_pos, dist_parent)
        cross_new_vec = self.cross_2d(self.delta_pos_start_end, delta_pos_parent, delta_pos)
        arc_angle_pred = np.radians(1) <= angle_parent <= np.radians(40)
        if parent_node.state == TrajectoryState.STAND_ON_1:
            if straight_angle_pred:
                return TrajectoryState.STAND_ON_1
            elif cross_new_vec <  0 and arc_angle_pred:
                return TrajectoryState.GIVE_WAY_ARC
            
        elif parent_node.state == TrajectoryState.GIVE_WAY_ARC:           
            if cross_new_vec < 0 and arc_angle_pred:
                return TrajectoryState.GIVE_WAY_ARC 
            elif cross_new_vec > 0 and arc_angle_pred:
                return TrajectoryState.GIVE_WAY_ARC_ADJUST
            
        elif parent_node.state == TrajectoryState.GIVE_WAY_ARC_ADJUST:  
            if straight_angle_pred:
                return TrajectoryState.STAND_ON_2         
            if cross_new_vec > 0 and arc_angle_pred:
                return TrajectoryState.GIVE_WAY_ARC_ADJUST 
            
        elif parent_node.state == TrajectoryState.STAND_ON_2:
            if straight_angle_pred:
                return TrajectoryState.STAND_ON_2
            elif cross_new_vec > 0 and arc_angle_pred:
                return TrajectoryState.RETURN_ARC 

        elif parent_node.state == TrajectoryState.RETURN_ARC:
            if cross_new_vec > 0 and arc_angle_pred:
                return TrajectoryState.RETURN_ARC 
            elif cross_new_vec < 0 and arc_angle_pred:
                return TrajectoryState.RETURN_ARC_ADJUST
            
        elif parent_node.state == TrajectoryState.RETURN_ARC_ADJUST:  
            if straight_angle_pred:
                return TrajectoryState.STAND_ON_3         
            if cross_new_vec < 0 and arc_angle_pred:
                return TrajectoryState.RETURN_ARC_ADJUST
            
        elif parent_node.state == TrajectoryState.STAND_ON_3:
            if straight_angle_pred:
                return TrajectoryState.STAND_ON_3   
            
        return None
        

