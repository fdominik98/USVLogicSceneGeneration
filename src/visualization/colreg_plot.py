import matplotlib.pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_config import *
import os
from model.colreg_situation import NoColreg
import matplotlib.image as mpimg
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from scipy.ndimage import rotate

colors = ['blue', 'red', 'green', 'orange', 'purple', 'grey', 'olive']
light_colors = ['lightblue', 'salmon', 'lightgreen', 'moccasin', 'thistle', 'lightgrey', 'y']

script_path = os.path.abspath(__file__)
current_dir = os.path.dirname(script_path)
img_dir = f'{current_dir}/../../assets/images'

class ColregPlot():  
    
    def __init__(self, env : USVEnvironment): 
        self.env = env
        self.dist_graphs = []
        self.vo_cone_graphs = []
        self.vo_cone_addition_graphs = []
        self.angle_circle_graphs = []
        self.legend_visible = True
        self.dist_visible = True   
        self.vo_cone_visible = False
        self.vo_cone_addition_visible = False
        self.angle_circle_visible = True
        
        self.image = mpimg.imread(f'{img_dir}/ship.png')
        
        #self.fig, self.ax = plt.subplots(figsize=(10, 10))      
        self.fig, (self.ax, self.lax) = plt.subplots(ncols=2, gridspec_kw={"width_ratios":[4, 1]}, figsize=(10,10))     
        self.draw()   
        
    def draw(self):
        # Create the plot            
        title = ''
        i = 0
        min_distances : dict[int, float]= {}
        for colreg_s in self.env.colreg_situations:
            if not isinstance(colreg_s, NoColreg): 
                line_break = '\n' if (i + 1) % 3 == 0 else ' '
                title = colreg_s.name if not title else f'{title},{line_break}{colreg_s.name}'
                i += 1
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2    
            
            if o1.id not in min_distances or min_distances[o1.id] > colreg_s.norm_p12:
                min_distances[o1.id] = colreg_s.norm_p12
            if o2.id not in min_distances or min_distances[o2.id] > colreg_s.norm_p12:
                min_distances[o2.id] = colreg_s.norm_p12
            
            text = self.ax.text(o1.p[0] + colreg_s.p12[0] / 2, o1.p[1] + colreg_s.p12[1] / 2, f'{colreg_s.norm_p12:.2f} m', fontsize=11, color='black')
            line, = self.ax.plot([o1.p[0], o2.p[0]], [o1.p[1], o2.p[1]], color=light_colors[5], linewidth=0.8, zorder=-3)
            self.dist_graphs += [text, line]
            
                
            vo_circle = plt.Circle(o2.p, colreg_s.r, color='black', fill=False, linestyle='--', linewidth=0.7)
            self.ax.add_artist(vo_circle)
            # Calculate the angles of the cone
            angle_rel = np.arctan2(colreg_s.p12[1], colreg_s.p12[0])
            angle1 = angle_rel + colreg_s.angle_half_cone
            angle2 = angle_rel - colreg_s.angle_half_cone
            
            # Plot the velocity obstacle cone
            cone1_vertex = o1.p
            cone11 = cone1_vertex + np.array([np.cos(angle1), np.sin(angle1)]) * colreg_s.norm_p12
            cone12 = cone1_vertex + np.array([np.cos(angle2), np.sin(angle2)]) * colreg_s.norm_p12
            line11, = self.ax.plot([o1.p[0], cone11[0]], [o1.p[1], cone11[1]], 'k--', linewidth=0.7)
            line12, = self.ax.plot([o1.p[0], cone12[0]], [o1.p[1], cone12[1]], 'k--', linewidth=0.7)    
            self.vo_cone_addition_graphs += [vo_circle, line11, line12]
            
            cone2_vertex = o2.v + o1.p
            cone21 = cone2_vertex + np.array([np.cos(angle1), np.sin(angle1)]) * colreg_s.norm_p12
            cone22 = cone2_vertex + np.array([np.cos(angle2), np.sin(angle2)]) * colreg_s.norm_p12

            line21, = self.ax.plot([o2.v[0] + o1.p[0], cone21[0]], [o2.v[1] + o1.p[1], cone21[1]], '--', color=colors[o2.id], linewidth=0.7)
            line22, = self.ax.plot([o2.v[0] + o1.p[0], cone22[0]], [o2.v[1] + o1.p[1], cone22[1]], '--', color=colors[o2.id], linewidth=0.7)
            self.vo_cone_graphs += [line21, line22]
            
            for g in self.vo_cone_addition_graphs + self.vo_cone_graphs:
                g.set_visible(False)  
              
                
            self.ax.quiver(o1.p[0], o1.p[1], o2.v[0], o2.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o2.id])
            colreg_s.info()
            
            
        for o in self.env.vessels:
            # Normalize the vector
            v_normalized = o.v / o.speed

            # Define the angle and radius
            angle_circle_slice_1 = HEAD_ON_ANGLE  # 20 degree slice
            angle_circle_slice_2 = OVERTAKE_ANGLE # 140 degree slice
            angle_circle_radius = min_distances[o.id] / 3
            circle_color = light_colors[o.id]

            circle = plt.Circle(o.p, angle_circle_radius, fill=False, color=circle_color, linewidth=0.8, zorder=-4)
            self.ax.add_artist(circle)

            # Draw two lines centered on the vector
            circle_line1 = self.draw_line(o.p, v_normalized, -angle_circle_slice_1 / 2, circle_color, angle_circle_radius)  # Left line
            circle_line2 = self.draw_line(o.p, v_normalized, angle_circle_slice_1 / 2, circle_color,  angle_circle_radius)   # Right line

            # Draw two lines centered on the negated vector
            circle_line3 = self.draw_line(o.p, -v_normalized, -angle_circle_slice_2 / 2, circle_color, angle_circle_radius)  # Left line
            circle_line4 = self.draw_line(o.p, -v_normalized, angle_circle_slice_2 / 2, circle_color, angle_circle_radius)   # Right line
            self.angle_circle_graphs += [circle, circle_line1, circle_line2, circle_line3, circle_line4]
            
            #self.ax.text(o.p[0] + o.r*1.5, o.p[1] + o.r*1.5, f'O{o.id}: ({o.p[0]:.2f}, {o.p[1]:.2f})\nv{o.id} speed: {o.speed:.2f} m/s', fontsize=11, color=colors[o.id], fontweight='bold')
            name = r'OS' if o.id == 0 else fr'$TS_{o.id}$'
            self.ax.text(o.p[0] + o.r, o.p[1] + o.r, name, color=colors[o.id], fontweight='bold')
            
            # Plot the positions and radii as circles
            circle = plt.Circle(o.p, o.r, color=colors[o.id], fill=False, linestyle='--', label=f'{name} Radius: {o.r}m')
            self.ax.add_artist(circle)

            # Plot vectors for better visibility
            v1_scaled = v_normalized * min_distances[o.id] / 4
            big_quiver = self.ax.quiver(o.p[0], o.p[1], v1_scaled[0], v1_scaled[1], angles='xy', scale_units='xy', scale=1, color=light_colors[o.id], zorder=-2)
            self.angle_circle_graphs += [big_quiver]
            angle = fr'$\theta = {self.vector_to_angle(o.v):.2f}^\circ$'
            speed = f'speed = {(o.speed / KNOT_TO_MS_CONVERSION):.2f}kn'
            # Plot the velocity vector with their actual lengths
            self.ax.quiver(o.p[0], o.p[1], o.v[0], o.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o.id], label=f'{name} Velocity: {angle}, {speed}')

            # Plot the positions
            self.ax.scatter(o.p[0], o.p[1], color=colors[o.id], s=100, label=f'{name} Position: ({o.p[0]:.2f}, {o.p[1]:.2f})')
            rotated_image = rotate(self.image, self.vector_to_angle(o.v)-90, reshape=True)
            imagebox = OffsetImage(rotated_image, zoom = 0.35, alpha=0.6)
            ab = AnnotationBbox(imagebox, o.p, frameon = False, zorder=-1)
            self.ax.add_artist(ab)
            
        self.fig.tight_layout(pad=5)
        self.ax.grid(False)
        #self.fig.legend(loc=7)
        #self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        h, l = self.ax.get_legend_handles_labels()
        self.lax.legend(h, l, loc=7)
        self.lax.axis("off")

        self.ax.set_title(f'USV situation ({title})')
        self.ax.set_xlabel('X Position (m)')
        self.ax.set_ylabel('Y Position (m)')
        self.ax.set_aspect('equal', adjustable='box')  
                
        # Get current x and y limits
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
        # Define a padding percentage (e.g., 5% of the range)
        x_padding = (x_max - x_min) * 0.05
        y_padding = (y_max - y_min) * 0.05
        # Set new limits with padding applied
        self.ax.set_xlim(x_min - x_padding, x_max + x_padding)
        self.ax.set_ylim(y_min - y_padding, y_max + y_padding)
        

        # Connect the key press event to the toggle function
        self.fig.canvas.mpl_connect('key_press_event', lambda e: self.toggle_visibility(e))

        plt.show(block=True)
        
    # Function to toggle the visibility
    def toggle_visibility(self, event):
        if event.key == '1':
            self.legend_visible = not self.legend_visible
            self.lax.set_visible(self.legend_visible)
        elif event.key == '2':
            self.dist_visible = not self.dist_visible
            for g in self.dist_graphs:
                g.set_visible(self.dist_visible)
        elif event.key == '5':
            self.vo_cone_visible = not self.vo_cone_visible
            for g in self.vo_cone_graphs:
                g.set_visible(self.vo_cone_visible)
        elif event.key == '4':
            self.vo_cone_addition_visible = not self.vo_cone_addition_visible
            for g in self.vo_cone_addition_graphs:
                g.set_visible(self.vo_cone_addition_visible)
        elif event.key == '3':
            self.angle_circle_visible = not self.angle_circle_visible
            for g in self.angle_circle_graphs:
                g.set_visible(self.angle_circle_visible)
        self.fig.canvas.draw()           
                
    # Function to draw lines for slices
    def draw_line(self, origin, center_vector, angle, color, length):
        direction = np.array([np.cos(angle), np.sin(angle)])
        rotation_matrix = np.array([[center_vector[0], -center_vector[1]],
                                    [center_vector[1],  center_vector[0]]])
        rotated_direction = rotation_matrix.dot(direction)
        end_point = origin + length * rotated_direction
        line, = self.ax.plot([origin[0], end_point[0]], [origin[1], end_point[1]], color=color, linewidth=0.8, zorder=-4)
        return line
    
    def vector_to_angle(self, v):
        # Calculate the angle in radians
        angle_radians = np.arctan2(v[1], v[0])
        
        # Convert the angle to degrees
        angle_degrees = np.degrees(angle_radians)
        
        # Normalize the angle to be between 0 and 360 degrees
        if angle_degrees < 0:
            angle_degrees += 360
        
        return angle_degrees