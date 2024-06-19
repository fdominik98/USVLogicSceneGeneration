import matplotlib.pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from model.usv_environment_config import USVEnvironmentConfig
from model.usv_config import *
import pickle
import os
from model.colreg_situation import NoConstraint

colors = ['blue', 'red', 'green', 'orange', 'purple', 'grey']
light_colors = ['lightblue', 'salmon', 'lightgreen', 'moccasin', 'thistle', 'lightgrey']

class ColregPlotFromFile():
    def __init__(self, env_config: USVEnvironmentConfig):
        # Load the best solutions from the file
        path = f'assets/{env_config.name}_sols.pkl'
        if not os.path.exists(path):
            return
        with open(path, 'rb') as f:
            loaded_solutions = pickle.load(f) 
            env = USVEnvironment(env_config)
        for sol in loaded_solutions:
            ColregPlot(env.update(sol))

class ColregPlot():    
    def __init__(self, env : USVEnvironment):       
        # Create the plot
        fig = plt.figure(figsize=(10, 10))        
            
        title = ''
        r_label = 'R Radius'
        cone_label = 'Velocity Obstacle Cone'
        for i, colreg_s in enumerate(env.colreg_situations):
            line_break = '\n' if (i + 1) % 3 == 0 else ' '
            title = colreg_s.name if not title else f'{title},{line_break}{colreg_s.name}'
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2      
            
            #'\nv1 angle to p1p2: {np.degrees(angle_p12_v1):.2f} degs'
            plt.text(o1.p[0] + colreg_s.p12[0] / 2, o1.p[1] + colreg_s.p12[1] / 2, f'Distance: {colreg_s.norm_p12:.2f} m', fontsize=11, color='black')
                
            plt.quiver(o1.p[0], o1.p[1], o2.v[0], o2.v[1], angles='xy', scale_units='xy', scale=1, color='red')
            circle = plt.Circle(o2.p, colreg_s.r, color='black', fill=False, linestyle='--', label=r_label)
            r_label = None
            
            plt.gca().add_artist(circle)
            if not isinstance(colreg_s, NoConstraint):
                # Calculate the angles of the cone
                angle_rel = np.arctan2(colreg_s.p12[1], colreg_s.p12[0])
                angle1 = angle_rel + colreg_s.angle_half_cone
                angle2 = angle_rel - colreg_s.angle_half_cone
                
                # Plot the velocity obstacle cone
                cone1_vertex = o1.p
                cone11 = cone1_vertex + np.array([np.cos(angle1), np.sin(angle1)]) * colreg_s.norm_p12
                cone12 = cone1_vertex + np.array([np.cos(angle2), np.sin(angle2)]) * colreg_s.norm_p12
                
                cone2_vertex = o2.v + o1.p
                cone21 = cone2_vertex + np.array([np.cos(angle1), np.sin(angle1)]) * colreg_s.norm_p12
                cone22 = cone2_vertex + np.array([np.cos(angle2), np.sin(angle2)]) * colreg_s.norm_p12

                #line11, = plt.plot([o1.p[0], cone11[0]], [o1.p[1], cone11[1]], 'k--')
                #line12, = plt.plot([o1.p[0], cone12[0]], [o1.p[1], cone12[1]], 'k--')            
            
                line21, = plt.plot([o2.v[0] + o1.p[0], cone21[0]], [o2.v[1] + o1.p[1], cone21[1]], 'k--', label=cone_label)
                cone_label = None
                line22, = plt.plot([o2.v[0] + o1.p[0], cone22[0]], [o2.v[1] + o1.p[1], cone22[1]], 'k--')
            
            plt.quiver(o1.p[0], o1.p[1], o2.v[0], o2.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o2.id])

            colreg_s.info()
            
            
        for o in env.vessels:
            plt.text(o.p[0] + o.r, o.p[1] + o.r, f'O{o.id}: ({o.p[0]:.2f}, {o.p[1]:.2f})\nv{o.id} speed: {o.speed:.2f} m/s', fontsize=11, color=colors[o.id])
            
            # Plot the positions and radii as circles
            circle = plt.Circle(o.p, o.r, color=colors[o.id], fill=False, linestyle='--', label=f'O{o.id} Radius')
            plt.gca().add_artist(circle)

            v1_scaled = o.v * visibility_range / o.speed / 4
            plt.quiver(o.p[0], o.p[1], v1_scaled[0], v1_scaled[1], angles='xy', scale_units='xy', scale=1, color=light_colors[o.id])
            
            # Plot the velocity vector with their actual lengths
            plt.quiver(o.p[0], o.p[1], o.v[0], o.v[1], angles='xy', scale_units='xy', scale=1, color=colors[o.id], label=f'O{o.id} Velocity')

            # Plot the positions
            plt.scatter(o.p[0], o.p[1], color=colors[o.id], s=100, label=f'O{o.id} Position')
            

        v1_scaled_norm = np.linalg.norm(v1_scaled)
        plt.xlim(min(env.vessels, key=lambda o: o.p[0]).p[0] - v1_scaled_norm, max(env.vessels, key=lambda o: o.p[0]).p[0] + v1_scaled_norm)
        plt.ylim(min(env.vessels, key=lambda o: o.p[1]).p[1] - v1_scaled_norm, max(env.vessels, key=lambda o: o.p[1]).p[1] + v1_scaled_norm)
        plt.axhline(0, color='grey', lw=0.5)
        plt.axvline(0, color='grey', lw=0.5)
        plt.grid(True)
        plt.legend()
        plt.title(f'USV situation ({title})')
        plt.xlabel('X Position (m)')
        plt.ylabel('Y Position (m)')
        plt.gca().set_aspect('equal', adjustable='box')

        plt.show()