from abc import ABC, abstractmethod
import random
from typing import List, Optional, Tuple
import pygame
import numpy as np
from model.vessel import Vessel
from trajectory_planning.path_interpolator import PathInterpolator

show_animation = True

DIM = 1200
windowSize = [DIM, DIM]

pygame.init()
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode(windowSize)
pygame.display.set_caption('Performing RRT')




class Node():
    """
    RRT Node
    """
    def __init__(self, p : np.ndarray):
        self.p = p
        self.distance_cost = 0.0
        self.time_cost : int = 0
        self.s_fraction = False
        self.parent : int = -1
        self.children : set[int] = set()
        
    @staticmethod
    def calc_cost(vessel : Vessel, d : float) -> Tuple[int, bool]:
        # Calculate the distance and heading between the points
        s_dist = int(d // vessel.speed)
        # Calculate the number of seconds required to cover the distance
        s_fraction = d / vessel.speed - s_dist
        if s_fraction > 0.0001:
            return s_dist + 1, True 
        return s_dist, False
    
    def set_cost(self, d : float, time : float, fraction : bool):
        self.distance_cost = d
        self.time_cost = time
        self.s_fraction = fraction       
        
class Obstacle(ABC):
    MARGIN = 0.02
    def __init__(self, x : float, y : float) -> None:
        super().__init__()
        self.p = np.array([x, y])
        
    @abstractmethod    
    def check_no_collision(self, node : Node) -> bool:
        pass
  
    
class CircularObstacle(Obstacle):
    def __init__(self, x : float, y : float, radius : float) -> None:
        super().__init__(x, y)
        self.radius = radius
        
    def check_no_collision(self, node : Node) -> bool:
        d = np.linalg.norm(node.p - self.p)
        if d <= self.radius + self.radius * self.MARGIN:
            return False  # collision
        return True  # safe
    
    
class LineObstacle(Obstacle):
    def __init__(self, x : float, y : float, dir_vec : np.ndarray, above_initial_point : bool, shift) -> None:
        super().__init__(x, y)
        self.shift = shift
        self.dir_vec = dir_vec
        self.above_initial_point = above_initial_point
        if above_initial_point:
            perpendicular = np.array([-dir_vec[1], dir_vec[0]])
        else:
            perpendicular = np.array([dir_vec[1], -dir_vec[0]])
            
        # Normalize the perpendicular vector
        self.perpendicular = perpendicular / np.linalg.norm(perpendicular)

        # Compute the shifted point on the line
        self.shifted_point = self.p + self.shift * self.perpendicular

        
    def check_no_collision(self, node : Node) -> bool:
        # Compute the cross product to determine the position relative to the shifted line
        # Line equation is implicit: (P - shifted_point) dotted with the perpendicular vector should be checked
        position_value = np.dot(self.perpendicular, node.p - self.shifted_point)

        if self.above_initial_point:
            if position_value > 0:
                return False # collision
            else:
                return True # safe
        else:
            if position_value < 0:
                return True # collision
            else:
                return False # safe
        # Determine if point is above or below the shifted line
    


class RRTStarFND():
    """
    Class for RRT Planning
    """
    def __init__(self, vessel : Vessel, start : np.ndarray, goal : np.ndarray,
                 obstacleList : List[Obstacle], randArea : List[Tuple[float, float]], 
                 collision_points : List[np.ndarray], interpolator : PathInterpolator,
                expandDis=10.0, goalSampleRate=15, maxIter=1500, scaler = 1.0):
        self.vessel = vessel
        self.collision_points = collision_points
        self.interpolator = interpolator
        self.start = Node(start)
        self.end = Node(goal)
        self.randArea = randArea
        self.expand_dist = expandDis
        self.goalSampleRate = goalSampleRate
        self.max_iter = maxIter
        self.obstacleList : List[Obstacle] = obstacleList
        self.current_i = 0
        self.stop = False
        self.scaler = scaler

    def do_plan(self, animation : bool) -> Optional[List[Node]]:
        while self.current_i < self.max_iter and not self.stop:
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
                        self.obstacleList.append(CircularObstacle(e.pos[0],e.pos[1], 400))
                        self.path_validation()
                    elif e.button == 3:
                        self.end.p[0] = e.pos[0]
                        self.end.p[1] = e.pos[1]
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
            while self.node_list[lastIndex].parent != -1:
                nodeInd = lastIndex
                lastIndex = self.node_list[lastIndex].parent
                dist, theta = self.get_d_theta(self.node_list[nodeInd], self.node_list[lastIndex])
                
                if not self.check_collision_extend(self.node_list[lastIndex].p, theta, dist):
                    self.node_list[lastIndex].children.discard(nodeInd)
                    self.remove_branch(nodeInd)
    
    
    def get_d_theta(self, node1 : Node, node2 : Node):
        delta_pos = node1.p - node2.p
        return np.linalg.norm(delta_pos), np.arctan2(delta_pos[1], delta_pos[0])

    def remove_branch(self, nodeInd):
        for ix in self.node_list[nodeInd].children:
            self.remove_branch(ix)
        self.node_list.pop(nodeInd)

    def choose_parent(self, newNode : Node, nearest_indexes):
        if len(nearest_indexes) == 0:
            return newNode

        distance_list = []
        for i in nearest_indexes:
            dist, theta = self.get_d_theta(newNode, self.node_list[i])
            if self.check_collision_extend(self.node_list[i].p, theta, dist):
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
        v = np.linalg.norm([rnd[0] - nearest_node.p[0], rnd[1] - nearest_node.p[1]])
        new_point = nearest_node.p + v * self.expand_dist
        new_node = Node(new_point)
        
        s_dist, s_fraction = Node.calc_cost(self.vessel, self.expand_dist)
        new_node.set_cost(nearest_node.distance_cost + self.expand_dist, nearest_node.time_cost + s_dist, s_fraction)
        new_node.parent = nearest_index
        return new_node

    def get_random_point(self):
        if random.randint(0, 100) > self.goalSampleRate:
            rnd = [random.uniform(*self.randArea[0]), random.uniform(*self.randArea[1])]
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

    def gen_final_course(self, goal_index : int):
        path = [self.end]
        while self.node_list[goal_index].parent != -1:
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

            d, theta = self.get_d_theta(new_node, near_node)

            new_cost = new_node.distance_cost + d

            if near_node.distance_cost > new_cost:
                if self.check_collision_extend(near_node.p, theta, d):
                    self.node_list[near_node.parent].children.discard(i)
                    near_node.parent = new_node_index
                    s_d, s_fraction = Node.calc_cost(self.vessel, d)
                    near_node.set_cost(new_cost, s_d + new_node.time_cost, s_fraction)
                    new_node.children.add(i)
                    

    def draw_graph(self, rnd=None):
        def reverse_coord(coords: np.ndarray):
            return np.array([(coords[0] - self.randArea[0][0]) * self.scaler  + 40, (DIM - (coords[1] - self.randArea[1][1])) * self.scaler])
        
        u"""
        Draw Graph
        """
        screen.fill((255, 255, 255))

        for o in self.obstacleList:
            if isinstance(o, LineObstacle):
                start = reverse_coord(o.shifted_point + o.dir_vec * 2 * DIM / self.scaler)
                end = reverse_coord(o.shifted_point - o.dir_vec * 2 * DIM / self.scaler)
                pygame.draw.line(screen,(0,0,0), start, end, 4)
                pygame.draw.circle(screen,(23,231,5), reverse_coord(o.shifted_point), 5) 
            elif isinstance(o, CircularObstacle):
                pygame.draw.circle(screen,(0,0,0), reverse_coord(o.p), o.radius * self.scaler)

        pygame.draw.circle(screen, (0,0,255), reverse_coord(self.start.p), 7)
        pygame.draw.circle(screen, (0,255,255), reverse_coord(self.end.p), 7)
        
        for cp in self.collision_points:
            pygame.draw.circle(screen,(255,0,0), reverse_coord(cp), 3)
            
        
        # Branches        
        for node in self.node_list.values():
            if node.parent != -1:
                pygame.draw.line(screen,(0,255,0), reverse_coord(self.node_list[node.parent].p), reverse_coord(node.p))
        for node in self.node_list.values():
            if len(node.children) == 0: 
                pygame.draw.circle(screen, (255,0,255), reverse_coord(node.p), 2)
                
        # Final path
        lastIndex = self.get_best_last_index()
        if lastIndex is not None:
            path = self.gen_final_course(lastIndex)

            ind = len(path)
            while ind > 1:
                pygame.draw.line(screen, (255,0,0), reverse_coord(path[ind-2]), reverse_coord(path[ind-1]))
                ind-=1
        

        pygame.display.update()


    def get_nearest_list_index(self, rnd):
        dist_list = np.subtract( np.array([ node.p for node in self.node_list.values() ]), (rnd[0],rnd[1]))**2
        dist_list = np.sum(dist_list, axis=1)
        min_index = list(self.node_list.keys())[np.argmin(dist_list)]
        return min_index


    def check_collision_extend(self, niP: np.ndarray, theta : float, d : float):
        tmpNode = Node(niP)

        for i in range(int(d/5)):
            tmpNode.p += np.array([5 * np.cos(theta), 5 * np.sin(theta)])
            if not self.check_no_collision(tmpNode, self.obstacleList):
                return False

        return True


    def check_no_collision(self, node : Node, obstacleList : List[Obstacle]):
        for obs in obstacleList:
            if not obs.check_no_collision(node):
                return False
            
        # The two trajectories will collide at the specific second
        for vessel, pos in self.interpolator.get_positions_by_second(node.time_cost):
            if np.linalg.norm(node.p - pos) <= (self.vessel.r + vessel.r) * 1.1:
                return False
        return True  # safe

