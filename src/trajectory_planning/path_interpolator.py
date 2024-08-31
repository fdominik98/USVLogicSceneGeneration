import numpy as np
from model.vessel import Vessel


class PathInterpolator():
    def __init__(self, o : Vessel, path : list[np.ndarray]) -> None:
        self.o = o
        self.path = path

    def interpolate_path(self) -> list[tuple[float,float,float,float]]:
        """
        Interpolates the given path to have positions at one-second intervals
        and calculates the heading based on the direction of movement.

        :param positions: List of (x, y) tuples representing the positions.
        :param speed: Speed of the vessel (units per second).
        :return: List of interpolated (position, heading) tuples.
        """
        interpolated_positions = [self.o.p]
        interpolated_headings = [self.o.heading]
        positions = self.path
        

        for i in range(len(positions) - 1):
            # Start and end points
            p_start = positions[i]
            p_end = positions[i + 1]
            
            # Calculate the distance and heading between the points
            delta_pos =  p_end - p_start
            d = np.linalg.norm(delta_pos)
            heading = np.arctan2(delta_pos[1], delta_pos[0])
            
            # Calculate the number of seconds required to cover the distance
            time_steps = int(d // self.o.speed)
            
            # Interpolate positions for each second
            for t in range(time_steps):
                fraction = t / time_steps
                new_p = p_start + delta_pos * fraction
                interpolated_positions.append(new_p)
                interpolated_headings.append(heading)
        
        # Append the final position and heading
        interpolated_positions.append(positions[-1])
        interpolated_headings.append(self.o.heading)
        
        result : list[tuple[float,float,float,float]] = []
        
        for i, heading in enumerate(interpolated_headings):
            pos = interpolated_positions[i]
            result.append((pos[0], pos[1], heading, self.o.speed))
        
        return result