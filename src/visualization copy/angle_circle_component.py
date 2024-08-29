from matplotlib import pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import BOW_ANGLE, MAX_COORD, STERN_ANGLE
from visualization.plot_component import PlotComponent, light_colors


class AngleCircleComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment, linewidth=0.8) -> None:
        super().__init__(ax, initial_visibility, env)
        self.linewidth = linewidth
            
    def do_draw(self, zorder : int):
        for o in self.env.vessels:
            # Define the angle and radius
            angle_circle_slice_1 = BOW_ANGLE  # 20 degree slice
            angle_circle_slice_2 = STERN_ANGLE # 140 degree slice
            angle_circle_radius = MAX_COORD / 10
            circle_color = light_colors[o.id]

            circle = plt.Circle(o.p, angle_circle_radius, fill=False, color=circle_color, linewidth=self.linewidth, zorder=zorder)
            self.ax.add_artist(circle)

            # Draw two lines centered on the vector
            circle_line1 = self.draw_line(o.p, o.v_norm(), -angle_circle_slice_1 / 2, circle_color, angle_circle_radius, zorder)  # Left line
            circle_line2 = self.draw_line(o.p, o.v_norm(), angle_circle_slice_1 / 2, circle_color,  angle_circle_radius, zorder)   # Right line

            # Draw two lines centered on the negated vector
            circle_line3 = self.draw_line(o.p, -o.v_norm(), -angle_circle_slice_2 / 2, circle_color, angle_circle_radius, zorder)  # Left line
            circle_line4 = self.draw_line(o.p, -o.v_norm(), angle_circle_slice_2 / 2, circle_color, angle_circle_radius, zorder)   # Right line
            
            # # Plot vectors for better visibility
            # v1_scaled = o.v_norm() * MAX_COORD / 11
            # big_quiver = self.ax.quiver(o.p[0], o.p[1], v1_scaled[0], v1_scaled[1], angles='xy', scale_units='xy', scale=1,
            #                             color=light_colors[o.id], zorder=zorder)
           
            #self.graphs += [circle, circle_line1, circle_line2, circle_line3, circle_line4, big_quiver]
            self.graphs += [circle, circle_line1, circle_line2, circle_line3, circle_line4]
      
            
    # Function to draw lines for slices
    def draw_line(self, origin, center_vector, angle, color, length, zorder):
        direction = np.array([np.cos(angle), np.sin(angle)])
        rotation_matrix = np.array([[center_vector[0], -center_vector[1]],
                                    [center_vector[1],  center_vector[0]]])
        rotated_direction = rotation_matrix.dot(direction)
        end_point = origin + length * rotated_direction
        line, = self.ax.plot([origin[0], end_point[0]], [origin[1], end_point[1]], color=color, linewidth=self.linewidth, zorder=zorder)
        return line
            