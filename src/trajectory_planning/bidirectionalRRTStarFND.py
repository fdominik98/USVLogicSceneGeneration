import random
from typing import List, Optional, Tuple
import pygame
import numpy as np
from model.vessel import Vessel
from trajectory_planning.rrt_utils import CircularObstacle, LineObstacle, Node, Obstacle
from trajectory_planning.path_interpolator import PathInterpolator

show_animation = True

DIM = 1200
windowSize = [DIM, DIM]

pygame.init()
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode(windowSize)
pygame.display.set_caption('Performing RRT')

class RRTStarFND():
    """
    Class for RRT Planning
    """
    def __init__(self, vessel : Vessel, start : np.ndarray, goal : np.ndarray,
                 obstacle_list : List[Obstacle], sample_area : List[Tuple[float, float]], 
                 collision_points : List[np.ndarray], interpolator : PathInterpolator,
                expand_dist=10.0, goal_sample_rate=15, max_iter=1500, scaler = 1.0):
        self.vessel = vessel
        self.collision_points = collision_points
        self.interpolator = interpolator
        self.start = Node(start)
        self.end = Node(goal)
        self.sample_area = sample_area
        self.expand_dist = expand_dist
        self.goal_sample_rate = goal_sample_rate
        self.max_iter = max_iter
        self.obstacleList : List[Obstacle] = obstacle_list
        self.current_i = 0
        self.stop = False
        self.scaler = scaler

    def do_plan(self, animation : bool) -> Optional[List[Node]]:
        while self.current_i < self.max_iter and not self.stop:
            if self.current_i % 100 == 0:
                print(self.current_i)

            rnd = self.get_random_point()
            nearest_index = self.get_nearest_list_index(rnd) # get nearest node index to random point
            new_node = self.steer(rnd, nearest_index) # generate new node from that nearest node in direction of random point

            if self.check_no_collision(new_node, self.obstacleList): # if it does not collide

                nearest_indexes = self.find_near_nodes(new_node, 5) # find nearest nodes to newNode
                new_node = self.choose_parent(new_node, nearest_indexes) # from that nearest nodes find the best parent to newNode
                self.node_list[self.current_i + 100] = new_node # add newNode to nodeList
                self.rewire(self.current_i + 100, new_node, nearest_indexes) # make newNode a parent of another node if necessary
                self.node_list[new_node.parent].children.add(self.current_i + 100)

                if len(self.node_list) > self.max_iter:
                    leaves = [ key for key, node in self.node_list.items() if len(node.children) == 0 and len(self.node_list[node.parent].children) > 1 ]
                    if len(leaves) > 1:
                        ind = leaves[random.randint(0, len(leaves)-1)]
                        self.node_list[self.node_list[ind].parent].children.discard(ind)
                        self.node_list.pop(ind)
                    else:
                        leaves = [ key for key, node in self.node_list.items() if len(node.children) == 0 ]
                        ind = leaves[random.randint(0, len(leaves)-1)]
                        self.node_list[self.node_list[ind].parent].children.discard(ind)
                        self.node_list.pop(ind)

            if animation and self.current_i % 25 == 0:
                self.draw_graph(rnd)

            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        coords = self.inverse_reverse_coord(np.array(e.pos))
                        self.obstacleList.append(CircularObstacle(*coords, 400))
                        self.path_validation()
                    elif e.button == 3:
                        self.end.p = self.inverse_reverse_coord(np.array(e.pos))
                        self.path_validation()
                elif e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_SPACE:
                            self.stop = True
                        
            self.current_i += 1
                        
        # generate coruse
        lastIndex = self.get_best_last_index()
        if lastIndex is None:
            return None
        path = self.gen_final_course(lastIndex)
        return path
        

    def plan_trajectory(self, animation=True) -> List[Node]:
        """
        plan_trajectory
        animation: flag for animation on or off
        """
        self.node_list = {0 : self.start}
        path = None
        while(path is None):
            path = self.do_plan(animation)
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

    def choose_parent(self, newNode : Node, nearest_indexes):
        if len(nearest_indexes) == 0:
            return newNode

        distance_list = []
        for i in nearest_indexes:
            no_coll, dist = self.check_no_collision_extend(self.node_list[i], newNode)
            if no_coll:
                distance_list.append(self.node_list[i].distance_cost + dist)
            else:
                distance_list.append(float("inf"))


        min_cost = min(distance_list)
        min_index = nearest_indexes[distance_list.index(min_cost)]

        if min_cost == float("inf"):
            print("min_cost is inf")
            return newNode

        newNode.distance_cost = min_cost
        newNode.parent = min_index
        return newNode

    def steer(self, rnd, nearest_index : int):
        # expand tree
        nearest_node = self.node_list[nearest_index]
        theta = np.arctan2(rnd[1] - nearest_node.p[1], rnd[0] - nearest_node.p[0])        
        new_point = nearest_node.p + np.array([np.cos(theta), np.sin(theta)]) * self.expand_dist
        new_node = Node(new_point)
        
        s_dist, s_fraction = Node.calc_cost(self.vessel, self.expand_dist)
        new_node.set_cost(nearest_node.distance_cost + self.expand_dist, nearest_node.time_cost + s_dist, s_fraction)
        new_node.parent = nearest_index
        return new_node

    def get_random_point(self):
        if random.randint(0, 100) > self.goal_sample_rate:
            rnd = [random.uniform(*self.sample_area[0]), random.uniform(*self.sample_area[1])]
        else:  # goal point sampling
            rnd = [self.end.p[0], self.end.p[1]]
        return rnd

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

    def find_near_nodes(self, newNode : Node, value):
        r = self.expand_dist * value

        distance_list = np.subtract( np.array([node.p for node in self.node_list.values()]), newNode.p)**2
        distance_list = np.sum(distance_list, axis=1)
        nearest_indexes = np.where(distance_list <= r ** 2)
        nearest_indexes = np.array(list(self.node_list.keys()))[nearest_indexes]
        return nearest_indexes
    

    def rewire(self, new_node_index : int, new_node : Node, near_indexes : List[int]):
        for i in near_indexes:
            near_node = self.node_list[i]

            d = np.linalg.norm(new_node.p - near_node.p)
            new_cost = new_node.distance_cost + d

            if near_node.distance_cost > new_cost:
                if self.check_no_collision_extend(near_node, new_node)[0]:
                    self.node_list[near_node.parent].children.discard(i)
                    near_node.parent = new_node_index
                    s_d, s_fraction = Node.calc_cost(self.vessel, d)
                    near_node.set_cost(new_cost, s_d + new_node.time_cost, s_fraction)
                    new_node.children.add(i)
                    
    
    def reverse_coord(self, coords: np.ndarray):
        return np.array([(coords[0] - self.sample_area[0][0]) * self.scaler + 50, DIM - (coords[1] - self.sample_area[1][0]) * self.scaler - 50])
    
    def inverse_reverse_coord(self, coords: np.ndarray):
        return np.array([(coords[0] - 50) / self.scaler + self.sample_area[0][0], (DIM - coords[1] - 50) / self.scaler + self.sample_area[1][0]])
    
    def draw_graph(self, rnd=None):
        
        u"""
        Draw Graph
        """
        screen.fill((255, 255, 255))

        for o in self.obstacleList:
            if isinstance(o, LineObstacle):
                start = self.reverse_coord(o.shifted_point + o.dir_vec * 2 * DIM / self.scaler)
                end = self.reverse_coord(o.shifted_point - o.dir_vec * 2 * DIM / self.scaler)
                pygame.draw.line(screen,(0,0,0), start, end, 4)
                pygame.draw.circle(screen,(23,231,5), self.reverse_coord(o.shifted_point), 5) 
            elif isinstance(o, CircularObstacle):
                pygame.draw.circle(screen,(0,0,0), self.reverse_coord(o.p), o.radius * self.scaler)

        pygame.draw.circle(screen, (0,0,255), self.reverse_coord(self.start.p), 7)
        pygame.draw.circle(screen, (0,255,255), self.reverse_coord(self.end.p), 7)
        
        for cp in self.collision_points:
            pygame.draw.circle(screen,(255,0,0), self.reverse_coord(cp), 3)
            
        
        # Branches        
        for node in self.node_list.values():
            if node.parent is not None:
                pygame.draw.line(screen,(0,255,0), self.reverse_coord(self.node_list[node.parent].p), self.reverse_coord(node.p))
        for node in self.node_list.values():
            if len(node.children) == 0: 
                pygame.draw.circle(screen, (255,0,255), self.reverse_coord(node.p), 2)
                
        # Final path
        lastIndex = self.get_best_last_index()
        if lastIndex is not None:
            path = self.gen_final_course(lastIndex)

            ind = len(path)
            while ind > 1:
                pygame.draw.line(screen, (255,0,0), self.reverse_coord(path[ind-2].p), self.reverse_coord(path[ind-1].p))
                ind-=1
        

        pygame.display.update()


    def get_nearest_list_index(self, rnd):
        dist_list = np.subtract( np.array([ node.p for node in self.node_list.values() ]), (rnd[0],rnd[1]))**2
        dist_list = np.sum(dist_list, axis=1)
        min_index = list(self.node_list.keys())[np.argmin(dist_list)]
        return min_index


    def check_no_collision_extend(self, parent_node : Node, node : Node) -> Tuple[bool, float]:
        tmpNode = Node(np.array([parent_node.p[0], parent_node.p[1]]))
        delta_pos = node.p - parent_node.p
        dist = float(np.linalg.norm(delta_pos))
        s_d, s_fraction = Node.calc_cost(self.vessel, dist)
        s_d = s_d - np.ceil(s_fraction)
        
        for s in range(int(s_d)):
            fraction = s / s_d
            tmpNode.p = parent_node.p + delta_pos * fraction
            tmpNode.set_cost(0, parent_node.time_cost + s, 0.0)
            if not self.check_no_collision(tmpNode, self.obstacleList):
                return False, dist
        return True, dist


    def check_no_collision(self, node : Node, obstacleList : List[Obstacle]):
        for obs in obstacleList:
            if not obs.check_no_collision(node):
                return False
            
        # The two trajectories will collide at the specific second
        for obs_vessel, pos in self.interpolator.get_positions_by_second(node.time_cost):
            if np.linalg.norm(node.p - pos) <= (self.vessel.r + obs_vessel.r) * 2:
                return False
        return True  # safe

