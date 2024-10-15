from typing import List
from matplotlib import pyplot as plt
import numpy as np
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_config import BOW_ANGLE, MAX_COORD, STERN_ANGLE
from model.vessel import Vessel
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, light_colors


class AngleCircleComponent(PlotComponent):
    # Define the angle and radius
    angle_circle_slice_1 = BOW_ANGLE  # 20 degree slice
    angle_circle_slice_2 = STERN_ANGLE # 140 degree slice
    
    def __init__(self, ax: plt.Axes, env : USVEnvironment, linewidth=0.8, radius_ratio = 10) -> None:
        super().__init__(ax, env)
        self.circle_graphs : List[plt.Circle] = []
        self.line1_graphs : List[plt.Line2D] = []
        self.line2_graphs : List[plt.Line2D] = []
        self.line3_graphs : List[plt.Line2D] = []
        self.line4_graphs : List[plt.Line2D] = []
        self.graphs_by_vessel = [self.circle_graphs, self.line1_graphs, self.line2_graphs, self.line3_graphs, self.line4_graphs]
        self.zorder = -20
        
        self.linewidth = linewidth
        self.angle_circle_radius = MAX_COORD / radius_ratio
            
    def do_draw(self):
        for o in self.env.vessels:
            self.one_draw(o, self.zorder, light_colors[o.id])
            
    
    def one_draw(self, o : Vessel,  zorder : int, circle_color):
        
        # Draw two lines centered on the vector
        circle_line1 = self.draw_line(o.p, o.v_norm(), -self.angle_circle_slice_1 / 2, circle_color, self.angle_circle_radius, zorder)  # Left line
        self.line1_graphs.append(circle_line1)
        circle_line2 = self.draw_line(o.p, o.v_norm(), self.angle_circle_slice_1 / 2, circle_color,  self.angle_circle_radius, zorder)   # Right line
        self.line2_graphs.append(circle_line2)
        
        # Draw two lines centered on the negated vector
        circle_line3 = self.draw_line(o.p, -o.v_norm(), -self.angle_circle_slice_2 / 2, circle_color, self.angle_circle_radius, zorder)  # Left line
        self.line3_graphs.append(circle_line3)
        circle_line4 = self.draw_line(o.p, -o.v_norm(), self.angle_circle_slice_2 / 2, circle_color, self.angle_circle_radius, zorder)   # Right line
        self.line4_graphs.append(circle_line4)
        
        # # Plot vectors for better visibility
        # v1_scaled = o.v_norm() * MAX_COORD / 11
        # big_quiver = self.ax.quiver(o.p[0], o.p[1], v1_scaled[0], v1_scaled[1], angles='xy', scale_units='xy', scale=1,
        #                             color=light_colors[o.id], zorder=zorder)
        
        #self.graphs += [circle, circle_line1, circle_line2, circle_line3, circle_line4, big_quiver]
        
        circle = plt.Circle(o.p, self.angle_circle_radius, fill=False, color=circle_color, linewidth=self.linewidth, zorder=zorder)
        self.ax.add_artist(circle)
        self.circle_graphs.append(circle)
        
        self.graphs += [circle, circle_line1, circle_line2, circle_line3, circle_line4]
        
      
    # Function to draw lines for slices
    def draw_line(self, origin, center_vector, angle, color, length, zorder):
        x, y = self.get_line_x_y(origin, center_vector, angle, length)
        line, = self.ax.plot(x, y, color=color, linewidth=self.linewidth, zorder=zorder)
        return line
    
    def get_line_x_y(self, origin, center_vector, angle, length):
        direction = np.array([np.cos(angle), np.sin(angle)])
        rotation_matrix = np.array([[center_vector[0], -center_vector[1]],
                                    [center_vector[1],  center_vector[0]]])
        rotated_direction = rotation_matrix.dot(direction)
        end_point = origin + length * rotated_direction
        return [origin[0], end_point[0]], [origin[1], end_point[1]]
            
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        for o in new_env.vessels:
            self.update_one(o)
            
        return self.graphs
    
    
    def update_one(self, o : Vessel):
        self.circle_graphs[o.id].set_center(o.p)
        self.circle_graphs[o.id].set_radius(self.angle_circle_radius)
        
        x1, y1 = self.get_line_x_y(o.p, o.v_norm(), -self.angle_circle_slice_1 / 2, self.angle_circle_radius)
        self.line1_graphs[o.id].set_data(x1, y1)
        
        x2, y2 = self.get_line_x_y(o.p, o.v_norm(), self.angle_circle_slice_1 / 2, self.angle_circle_radius)
        self.line2_graphs[o.id].set_data(x2, y2)
        
        x3, y3 = self.get_line_x_y(o.p, -o.v_norm(), -self.angle_circle_slice_2 / 2, self.angle_circle_radius)
        self.line3_graphs[o.id].set_data(x3, y3)
        
        x4, y4 = self.get_line_x_y(o.p, -o.v_norm(), self.angle_circle_slice_2 / 2, self.angle_circle_radius)
        self.line4_graphs[o.id].set_data(x4, y4)
    