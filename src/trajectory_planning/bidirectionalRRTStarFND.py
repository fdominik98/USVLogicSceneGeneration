from abc import ABC, abstractmethod
import random
from typing import Optional
import pygame
import timeit, time
import numpy as np
show_animation = True

DIM = 1000
windowSize = [DIM, DIM]

pygame.init()
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode(windowSize)
pygame.display.set_caption('Performing RRT')




class Node():
    """
    RRT Node
    """
    def __init__(self, x : float, y : float):
        self.p = np.array([x, y])
        self.cost = 0.0
        self.parent : Optional[int] = None
        self.children : set[int] = set()
        
        
class Obstacle(ABC):
    MARGIN = 0.05
    def __init__(self, x : float, y : float) -> None:
        super().__init__()
        self.p = np.array([x, y])
        
    @abstractmethod    
    def no_collision_check(self, node : Node) -> bool:
        pass
  
    
class CircularObstacle(Obstacle):
    def __init__(self, x : float, y : float, radius : float) -> None:
        super().__init__(x, y)
        self.radius = radius
        
    def no_collision_check(self, node : Node) -> bool:
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

        
    def no_collision_check(self, node : Node) -> bool:
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
    def __init__(self, start, goal, obstacleList : list[Obstacle],
                 randArea, expandDis=10.0, goalSampleRate=15, maxIter=1500):

        self.start = Node(start[0], start[1])
        self.end = Node(goal[0], goal[1])
        self.Xrand = randArea[0]
        self.Yrand = randArea[1]
        self.expandDis = expandDis
        self.goalSampleRate = goalSampleRate
        self.maxIter = maxIter
        self.obstacleList : list[Obstacle] = obstacleList
        self.current_i = 0

    def do_plan(self, animation : bool) -> Optional[list[np.ndarray]]:
        while self.current_i < self.maxIter:
            print(self.current_i)

            rnd = self.get_random_point()
            nind = self.GetNearestListIndex(rnd) # get nearest node index to random point
            newNode = self.steer(rnd, nind) # generate new node from that nearest node in direction of random point

            if self.__CollisionCheck(newNode, self.obstacleList): # if it does not collide

                nearinds = self.find_near_nodes(newNode, 5) # find nearest nodes to newNode
                newNode = self.choose_parent(newNode, nearinds) # from that nearest nodes find the best parent to newNode
                self.nodeList[self.current_i + 100] = newNode # add newNode to nodeList
                self.rewire(self.current_i + 100, newNode, nearinds) # make newNode a parent of another node if necessary
                self.nodeList[newNode.parent].children.add(self.current_i + 100)

                if len(self.nodeList) > self.maxIter:
                    leaves = [ key for key, node in self.nodeList.items() if len(node.children) == 0 and len(self.nodeList[node.parent].children) > 1 ]
                    if len(leaves) > 1:
                        ind = leaves[random.randint(0, len(leaves)-1)]
                        self.nodeList[self.nodeList[ind].parent].children.discard(ind)
                        self.nodeList.pop(ind)
                    else:
                        leaves = [ key for key, node in self.nodeList.items() if len(node.children) == 0 ]
                        ind = leaves[random.randint(0, len(leaves)-1)]
                        self.nodeList[self.nodeList[ind].parent].children.discard(ind)
                        self.nodeList.pop(ind)

            if animation and self.current_i % 25 == 0:
                self.DrawGraph(rnd)

            for e in pygame.event.get():
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        self.obstacleList.append(CircularObstacle(e.pos[0],e.pos[1], 50))
                        self.path_validation()
                    elif e.button == 3:
                        self.end.p[0] = e.pos[0]
                        self.end.p[1] = e.pos[1]
                        self.path_validation()
                        
            self.current_i += 1
                        
        # generate coruse
        lastIndex = self.get_best_last_index()
        if lastIndex is None:
            return None
        path = self.gen_final_course(lastIndex)
        return path
        

    def Planning(self, animation=True) -> list[np.ndarray]:
        """
        Pathplanning
        animation: flag for animation on or off
        """
        self.nodeList = {0 : self.start}
        path = None
        while(path is None):
            path = self.do_plan(animation)
            if path is None:
                self.maxIter += 100
                print("No solution repeating for 100 more iterations.")
        path.reverse()
        return path     

    def path_validation(self):
        lastIndex = self.get_best_last_index()
        if lastIndex is not None:
            while self.nodeList[lastIndex].parent is not None:
                nodeInd = lastIndex
                lastIndex = self.nodeList[lastIndex].parent
                d, theta = self.get_d_theta(self.nodeList[nodeInd], self.nodeList[lastIndex])
                
                if not self.check_collision_extend(self.nodeList[lastIndex].p, theta, d):
                    self.nodeList[lastIndex].children.discard(nodeInd)
                    self.remove_branch(nodeInd)
    
    
    def get_d_theta(self, node1 : Node, node2 : Node):
        delta_pos = node1.p - node2.p
        return np.linalg.norm(delta_pos), np.arctan2(delta_pos[1], delta_pos[0])

    def remove_branch(self, nodeInd):
        for ix in self.nodeList[nodeInd].children:
            self.remove_branch(ix)
        self.nodeList.pop(nodeInd)

    def choose_parent(self, newNode : Node, nearinds):
        if len(nearinds) == 0:
            return newNode

        dlist = []
        for i in nearinds:
            d, theta = self.get_d_theta(newNode, self.nodeList[i])
            if self.check_collision_extend(self.nodeList[i].p, theta, d):
                dlist.append(self.nodeList[i].cost + d)
            else:
                dlist.append(float("inf"))


        mincost = min(dlist)
        minind = nearinds[dlist.index(mincost)]

        if mincost == float("inf"):
            print("mincost is inf")
            return newNode

        newNode.cost = mincost
        newNode.parent = minind
        return newNode

    def steer(self, rnd, nind):
        # expand tree
        nearestNode = self.nodeList[nind]
        theta = np.arctan2(rnd[1] - nearestNode.p[1], rnd[0] - nearestNode.p[0])
        newNode = Node(nearestNode.p[0], nearestNode.p[1])
        newNode.p += np.array([np.cos(theta), np.sin(theta)]) * self.expandDis

        newNode.cost = nearestNode.cost + self.expandDis
        newNode.parent = nind 
        return newNode

    def get_random_point(self):
        if random.randint(0, 100) > self.goalSampleRate:
            rnd = [random.uniform(0, self.Xrand), random.uniform(0, self.Yrand)]
        else:  # goal point sampling
            rnd = [self.end.p[0], self.end.p[1]]
        return rnd

    def get_best_last_index(self):
        disglist = [(key, np.linalg.norm(self.end.p - node.p)) for key, node in self.nodeList.items()]
        goalinds = [key for key, distance in disglist if distance <= self.expandDis]

        if len(goalinds) == 0:
            return None

        mincost = min([self.nodeList[key].cost for key in goalinds])
        for i in goalinds:
            if self.nodeList[i].cost == mincost:
                return i

        return None

    def gen_final_course(self, goalind : int):
        path = [self.end.p]
        while self.nodeList[goalind].parent is not None:
            node = self.nodeList[goalind]
            path.append(node.p)
            goalind = node.parent
        path.append(self.start.p)
        return path

    def find_near_nodes(self, newNode : Node, value):
        r = self.expandDis * value

        dlist = np.subtract( np.array([node.p for node in self.nodeList.values()]), newNode.p)**2
        dlist = np.sum(dlist, axis=1)
        nearinds = np.where(dlist <= r ** 2)
        nearinds = np.array(list(self.nodeList.keys()))[nearinds]

        return nearinds

    def rewire(self, newNodeInd : int, newNode : Node, nearinds : list[int]):
        nnode = len(self.nodeList)
        for i in nearinds:
            nearNode = self.nodeList[i]

            d, theta = self.get_d_theta(newNode, nearNode)

            scost = newNode.cost + d

            if nearNode.cost > scost:
                if self.check_collision_extend(nearNode.p, theta, d):
                    self.nodeList[nearNode.parent].children.discard(i)
                    nearNode.parent = newNodeInd
                    nearNode.cost = scost
                    newNode.children.add(i)

    def check_collision_extend(self, niP: np.ndarray, theta : float, d : float):
        tmpNode = Node(niP[0], niP[1])

        for i in range(int(d/5)):
            tmpNode.p += np.array([5 * np.cos(theta), 5 * np.sin(theta)])
            if not self.__CollisionCheck(tmpNode, self.obstacleList):
                return False

        return True

    def DrawGraph(self, rnd=None):
        u"""
        Draw Graph
        """
        screen.fill((255, 255, 255))
        for node in self.nodeList.values():
            if node.parent is not None:
                pygame.draw.line(screen,(0,255,0), self.nodeList[node.parent].p, node.p)

        for node in self.nodeList.values():
            if len(node.children) == 0: 
                pygame.draw.circle(screen, (255,0,255), node.p, 2)
                

        for o in self.obstacleList:
            if isinstance(o, LineObstacle):
                pygame.draw.line(screen,(0,0,0), o.shifted_point + o.dir_vec*10000, o.shifted_point - o.dir_vec*10000, 5)
            elif isinstance(o, CircularObstacle):
                pygame.draw.circle(screen,(0,0,0), o.p, o.radius)

        pygame.draw.circle(screen, (255,0,0), self.start.p, 10)
        pygame.draw.circle(screen, (0,0,255), self.end.p, 10)

        lastIndex = self.get_best_last_index()
        if lastIndex is not None:
            path = self.gen_final_course(lastIndex)

            ind = len(path)
            while ind > 1:
                pygame.draw.line(screen,(255,0,0),path[ind-2],path[ind-1])
                ind-=1

        pygame.display.update()


    def GetNearestListIndex(self, rnd):
        dlist = np.subtract( np.array([ node.p for node in self.nodeList.values() ]), (rnd[0],rnd[1]))**2
        dlist = np.sum(dlist, axis=1)
        minind = list(self.nodeList.keys())[np.argmin(dlist)]
        return minind

    def __CollisionCheck(self, node : Node, obstacleList : list[Obstacle]):
        for o in obstacleList:
            if not o.no_collision_check(node):
                return False
        return True  # safe



def main():
    print("start RRT path planning")

    # ====Search Path with RRT====
    obstacleList = [
        CircularObstacle(215, 300, 120),
        CircularObstacle(380, 300, 40),
    ]  # [x,y,size]
    # Set Initial parameters
    rrt = RRTStarFND(start=[20, 300], goal=[700, 300],
              randArea=[DIM, DIM], obstacleList=obstacleList)
    path = rrt.Planning(animation=show_animation)


if __name__ == '__main__':
    main()