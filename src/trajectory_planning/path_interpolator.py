from typing import Dict, List, Tuple
import numpy as np
from model.vessel import Vessel
from model.usv_environment import USVEnvironment


class PathInterpolator():
    def __init__(self, env: USVEnvironment) -> None:
        self.env = env
        self.interpolated_paths : Dict[int, List[Tuple[float,float,float,float]]] = {}
        self.path_length = 45 * 60

    def add_path(self, vessel : Vessel, path : List[np.ndarray]):
        if vessel.id in self.interpolated_paths:
            raise Exception("Cannot add two path for one vessel")
        if len(path) == 0:
            self.interpolated_paths[vessel.id] = [(vessel.p[0], vessel.p[1], vessel.heading, vessel.speed)]
        else:
            self.interpolate_path(vessel, path)
        self.extend_paths_to_path_length()       
    
           
                
    def extend_paths_to_path_length(self):
        for id, path in self.interpolated_paths.items():
            o = self.env.get_vessel_by_id(id)
            while len(path) < self.path_length:
                # Lengthen path
                last_state = path[-1]
                path.append((
                    last_state[0] + o.v[0],
                    last_state[1] + o.v[1],
                    o.heading,
                    o.speed
                ))
                
    def get_positions_by_second(self, second) -> List[Tuple[Vessel, np.ndarray]]:
        if second <= self.path_length:
            self.path_length = second + 50
            self.extend_paths_to_path_length()
        return [(self.env.get_vessel_by_id(id), path[second]) for id, path in self.interpolated_paths.items()]
                

    def interpolate_path(self, vessel: Vessel, path : List[np.ndarray]) -> List[Tuple[float,float,float,float]]:
        """
        Interpolates the given path to have positions at one-second intervals
        and calculates the heading based on the direction of movement.

        :param positions: List of (x, y) tuples representing the positions.
        :param speed: Speed of the vessel (units per second).
        :return: List of interpolated (position, heading) tuples.
        """
        interpolated_positions = []
        interpolated_headings = []
        interpolated_speeds = []
        

        for i in range(len(path) - 1):
            # Start and end points
            p_start = path[i]
            p_end = path[i + 1]
            
            # Calculate the distance and heading between the points
            delta_pos =  p_end - p_start
            heading = np.arctan2(delta_pos[1], delta_pos[0])
            d = np.linalg.norm(delta_pos)
            
            seconds_per_expand = int(d // vessel.speed)
            # Calculate the number of seconds required to cover the distance
            fraction_second = d / vessel.speed - seconds_per_expand
            if fraction_second > 0.0001:
                seconds_per_expand += 1
                
            
            # Interpolate positions for each second
            for t in range(seconds_per_expand):
                fraction = t / seconds_per_expand
                new_p = p_start + delta_pos * fraction
                interpolated_positions.append(new_p)
                interpolated_headings.append(heading)
                interpolated_speeds.append(vessel.speed)                
            if fraction_second > 0.0001: # Bigger than some small value
                speed = vessel.speed * fraction_second
                interpolated_speeds[-1] = speed 
        
        # Append the final position and heading
        interpolated_positions.append(path[-1])
        interpolated_headings.append(vessel.heading)
        interpolated_speeds.append(vessel.speed)
        
        result : List[Tuple[float,float,float,float]] = []
        
        for i, heading in enumerate(interpolated_headings):
            pos = interpolated_positions[i]
            speed = interpolated_speeds[i]
            result.append((pos[0], pos[1], heading, speed))
        
        return result
    
    @staticmethod
    def interpolate_headings(trajectory : List[Tuple[float,float,float,float]])  -> List[Tuple[float,float,float,float]]:
        headings = [t[2] for t in trajectory]
        def interpolate_chunk(start, end, num_steps):
            """Linearly interpolate between start and end in num_steps steps."""
            step_values = []
            for i in range(num_steps):
                ratio = i / (num_steps - 1) if num_steps > 1 else 0
                interpolated_value = start * (1 - ratio) + end * ratio
                step_values.append(interpolated_value)
            return step_values

        # Find blocks of same heading
        blocks = []
        current_block = [0]
        for i in range(1, len(headings)):
            if headings[i] == headings[current_block[0]]:
                current_block.append(i)
            else:
                blocks.append(current_block)
                current_block = [i]
        blocks.append(current_block)

        # Interpolate between the end of one block to the start of the next
        for i in range(len(blocks) - 1):
            start_block = blocks[i]
            end_block = blocks[i + 1]
            
            start_value = headings[start_block[-1]]
            end_value = headings[end_block[0]]
            
            # Interpolate from the last index of the current block to the first index of the next block
            num_steps = len(start_block) + len(end_block)
            interpolated_values = interpolate_chunk(start_value, end_value, num_steps)
            
            # Replace values in the original list
            for j in range(len(start_block)):
                headings[start_block[j]] = interpolated_values[j]
            for j in range(len(end_block)):
                headings[end_block[j]] = interpolated_values[len(start_block) + j]
        
        return [(trajectory[i][0], trajectory[i][1], headings[i], trajectory[i][3]) for i in range(len(headings))]