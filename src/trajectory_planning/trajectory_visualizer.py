from typing import List, Optional, Tuple
import numpy as np
from trajectory_planning.path_interpolator import PathInterpolator
from trajectory_planning.rrt_utils import CircularObstacle, LineObstacle, Obstacle, PolygonalObstacle, TrajectoryState, Node
import pygame
from trajectory_planning.vessel_order_graph import VesselNode

class TrajectoryVisualizer():
    def __init__(self, dim : int, scaler : float, sample_area : List[Tuple[float, float]]) -> None:
        self.scaler = scaler
        self.sample_area = sample_area
        self.dim = dim
        window_size = [dim, dim]
        pygame.init()
        self.screen = pygame.display.set_mode(window_size)
        
    
    def set_caption(self, v_node : VesselNode, interpolator : PathInterpolator):
        conf_colregs = ""
        for colreg_s in v_node.colreg_situations:           
            conf_colregs = colreg_s.name if not conf_colregs else f'{conf_colregs}, {colreg_s.name}'
        
        conf_trajs = ""
        for obs_vessel in interpolator.vessels.values():
             conf_trajs = obs_vessel.name if not conf_trajs else f'{conf_trajs}, {obs_vessel.name}'
            
        pygame.display.set_caption(f'{conf_colregs}, Conflicting trajectories: {conf_trajs}')
        
    
    def draw_obstacles(self, obstacle_list : List[Obstacle], collision_points : List[np.ndarray]):
        for o in obstacle_list:
            if isinstance(o, LineObstacle):
                start = self.reverse_coord(o.shifted_point + o.dir_vec * 2 * self.dim / self.scaler)
                end = self.reverse_coord(o.shifted_point - o.dir_vec * 2 * self.dim / self.scaler)
                pygame.draw.line(self.screen,(0,0,0), start, end, 4)
                pygame.draw.circle(self.screen,(23,231,5), self.reverse_coord(o.shifted_point), 5) 
            elif isinstance(o, CircularObstacle):
                pygame.draw.circle(self.screen,(255,0,0), self.reverse_coord(o.p), o.radius * self.scaler, width=5)
            elif isinstance(o, PolygonalObstacle):
                pygame.draw.polygon(self.screen, (0,0,0), [self.reverse_coord(p) for p in o.polygon])

        for cp in collision_points:
            pygame.draw.circle(self.screen,(255,0,0), self.reverse_coord(cp), 3)
            
        
    def draw_branches(self, start : Node, end : Node, node_list : dict[int, Node], last_index : Optional[int], gen_final_course):
        pygame.draw.circle(self.screen, (0,0,255), self.reverse_coord(start.p), 7)
        pygame.draw.circle(self.screen, (0,255,255), self.reverse_coord(end.p), 7)
        # Branches        
        for node in node_list.values():
            if node.parent is not None:
                pygame.draw.line(self.screen,(0,255,0), self.reverse_coord(node_list[node.parent].p), self.reverse_coord(node.p))
        for node in node_list.values():
            if len(node.children) == 0: 
                pygame.draw.circle(self.screen, (255,0,255), self.reverse_coord(node.p), 2)
                
        # Final path
        if last_index is not None:
            path : List[Node] = gen_final_course(last_index)

            ind = len(path)
            while ind > 1:
                if (path[ind-2].state is TrajectoryState.STAND_ON_1 or
                    path[ind-2].state is TrajectoryState.STAND_ON_2 or
                    path[ind-2].state is TrajectoryState.STAND_ON_3):
                    color = (255,0, 0)
                elif path[ind-2].state is TrajectoryState.START:
                    color = (0, 0, 0)
                elif path[ind-2].state is TrajectoryState.GIVE_WAY_ARC:
                    color = (0, 0, 255)
                elif path[ind-2].state is TrajectoryState.GIVE_WAY_ARC_ADJUST:
                    color = (0, 100, 255)
                elif path[ind-2].state is TrajectoryState.RETURN_ARC:
                    color = (0, 180, 255)
                elif path[ind-2].state is TrajectoryState.RETURN_ARC_ADJUST:
                    color = (0, 255, 255)
                else:
                    color = (255,255,255)
                pygame.draw.line(self.screen, color, self.reverse_coord(path[ind-2].p), self.reverse_coord(path[ind-1].p), 5)
                ind-=1

    def update(self, obstacle_list : List[Obstacle], collision_points : List[np.ndarray],
               start : Node, end : Node, node_list : dict[int, Node], last_index : Optional[int], gen_final_course):
        self.screen.fill((255, 255, 255))
        self.draw_obstacles(obstacle_list, collision_points)
        self.draw_branches(start, end, node_list, last_index, gen_final_course)
        pygame.display.update()
        
        
    def handle_user_input(self, end : Node, obstacle_list : List[Obstacle], path_validation) -> bool:
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    coords = self.inverse_reverse_coord(np.array(e.pos))
                    obstacle_list.append(CircularObstacle(coords, 400))
                    path_validation()
                elif e.button == 3:
                    end.p = self.inverse_reverse_coord(np.array(e.pos))
                    path_validation()
            elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE:
                        return True
                    elif e.key == pygame.K_ESCAPE:
                        exit(0)
        return False
                        
                    
    def reverse_coord(self, coords: np.ndarray):
        return np.array([(coords[0] - self.sample_area[0][0]) * self.scaler + 50, self.dim - (coords[1] - self.sample_area[1][0]) * self.scaler - 50])
    
    def inverse_reverse_coord(self, coords: np.ndarray):
        return np.array([(coords[0] - 50) / self.scaler + self.sample_area[0][0], (self.dim - coords[1] - 50) / self.scaler + self.sample_area[1][0]])
    
