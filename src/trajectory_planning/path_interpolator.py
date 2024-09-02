import numpy as np
from model.vessel import Vessel


class PathInterpolator():
    def __init__(self, vessels : list[Vessel], expand_distance : float) -> None:
        self.vessels = vessels
        self.paths :  dict[int, list[list[np.ndarray]]] = {}
        self.interpolated_paths : dict[int, list[tuple[float,float,float,float]]] = {}

    def add_path(self, vessel : Vessel, path : list[np.ndarray]):
        if vessel.id in self.paths:
            self.paths[vessel.id].append(path)
        else:
            self.paths[vessel.id] = [path]
            
            
    def interpolate(self):
        for vessel in self.vessels:
            # Interpolate the longest path in case of multiple path. Other strategy can be used also
            # If a vessel is give-way and stand on in the same time, give-way is prioritized
            longest_path = max(self.paths[vessel.id], key=len)  
                      
            if len(longest_path) == 0:
                self.interpolated_paths[vessel.id] = [(vessel.p[0], vessel.p[1], vessel.heading, vessel.speed)]
                continue
            self.interpolated_paths[vessel.id] = self.interpolate_path(vessel, longest_path)
            
        longest_key = max(self.interpolated_paths, key=lambda k: len(self.interpolated_paths[k]))
        # Find the interpolated longest path length
        longest_ipath_length = len(self.interpolated_paths[longest_key])
        for vessel in self.vessels:
            interpolated_path = self.interpolated_paths[vessel.id]
            while len(interpolated_path) < longest_ipath_length:
                # Lengthen path
                last_state = interpolated_path[-1]
                interpolated_path.append((
                    last_state[0] + vessel.v[0],
                    last_state[1] + vessel.v[1],
                    vessel.heading,
                    vessel.speed
                ))
                

    def interpolate_path(self, vessel: Vessel, path : list[np.ndarray]) -> list[tuple[float,float,float,float]]:
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
        
        interpolated_headings = self.interpolate_headings(interpolated_headings)
        
        result : list[tuple[float,float,float,float]] = []
        
        for i, heading in enumerate(interpolated_headings):
            pos = interpolated_positions[i]
            speed = interpolated_speeds[i]
            result.append((pos[0], pos[1], heading, speed))
        
        return result
    
    
    def interpolate_headings(self, headings):
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
        
        return headings