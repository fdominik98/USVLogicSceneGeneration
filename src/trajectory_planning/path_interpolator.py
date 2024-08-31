import numpy as np
from model.vessel import Vessel


class PathInterpolator():
    def __init__(self, vessels : list[Vessel],) -> None:
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
        interpolated_positions = [vessel.p]
        interpolated_headings = [vessel.heading]

        for i in range(len(path) - 1):
            # Start and end points
            p_start = path[i]
            p_end = path[i + 1]
            
            # Calculate the distance and heading between the points
            delta_pos =  p_end - p_start
            d = np.linalg.norm(delta_pos)
            heading = np.arctan2(delta_pos[1], delta_pos[0])
            
            # Calculate the number of seconds required to cover the distance
            time_steps = int(d // vessel.speed)
            
            # Interpolate positions for each second
            for t in range(time_steps):
                fraction = t / time_steps
                new_p = p_start + delta_pos * fraction
                interpolated_positions.append(new_p)
                interpolated_headings.append(heading)
        
        # Append the final position and heading
        interpolated_positions.append(path[-1])
        interpolated_headings.append(vessel.heading)
        
        result : list[tuple[float,float,float,float]] = []
        
        for i, heading in enumerate(interpolated_headings):
            pos = interpolated_positions[i]
            result.append((pos[0], pos[1], heading, vessel.speed))
        
        return result