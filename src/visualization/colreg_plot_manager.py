import tkinter as tk
from typing import Dict, List, Optional, Tuple
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from model.usv_environment import USVEnvironment
from visualization.colreg_animation import ANIM_REAL_TIME, ANIM_SIM_TIME, TWO_HOURS, TWO_MINUTES
from visualization.plot_component import light_colors
from visualization.colreg_plot import ColregPlot

class StandaloneCheckbox:
    def __init__(self, master, artists: List[plt.Artist], color, init_checked : bool, canvas : Optional[FigureCanvasTkAgg] = None, text = ''):
        self.artists = artists
        self.text = text
        self.canvas = canvas
        self.value = tk.BooleanVar(master=master, value=init_checked)  # BooleanVar linked to checkbox
        self.checkbox = tk.Checkbutton(
            master,
            variable=self.value,  # Correctly linked variable
            onvalue=True,
            text=text,
            offvalue=False,
            command=self.on_click,  # Calls show_selection when clicked
            background=color
        )
        self.checkbox.pack(side=tk.TOP, anchor='w', fill=tk.NONE)
        self.set_state(init_checked)

    def on_click(self):
        if self.canvas is not None:
            self.set_state(self.value.get())
            self.canvas.draw_idle()
        
    def set_state(self, state : bool):
        self.value.set(state)
        for a in self.artists:
            a.set_visible(state)
class CheckboxArray:
    def __init__(self, master, text: str, canvas: FigureCanvasTkAgg):
        self.canvas = canvas
        self.managed_checkboxes : List[Checkbox]= []
        self.value = tk.BooleanVar(master=master, value=False)  # BooleanVar linked to checkbox
        self.checkbox = tk.Checkbutton(
            master,
            text=text,
            variable=self.value,  # Correctly linked variable
            onvalue=True,
            offvalue=False,
            command=self.on_click,  # Calls show_selection when clicked,
            background='grey'
        )
        self.checkbox.pack(side=tk.TOP, anchor='w')
        
    def add(self, cb):
        self.managed_checkboxes.append(cb)
        self.notify()

    def on_click(self):
        state = self.value.get()
        for cb in self.managed_checkboxes:
            cb.set_state(state)
        self.canvas.draw_idle()
    
    def notify(self):
        all_false = all(cb.value.get() == False for cb in self.managed_checkboxes)
        self.value.set(not all_false)
        self.canvas.draw_idle()
        
class Checkbox(StandaloneCheckbox):
    def __init__(self, master, artists: List[plt.Artist], checkbox_array : CheckboxArray, color : str, init_checked : bool):
        super().__init__(master, artists, color, init_checked)
        self.checkbox_array = checkbox_array
        self.checkbox_array.add(self)

    def on_click(self):
        self.set_state(self.value.get())
        self.checkbox_array.notify()       
        

class ColregPlotManager():
    def __init__(self, env : USVEnvironment,
                 trajectories : Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None): 
        self.colreg_plot = ColregPlot(env, False, trajectories)  
        self.env = env
        root = tk.Tk()
        root.option_add("*Font", ("Times New Roman", 14))
        
        root.title("COLREG situation visualizer")

        # CANVAS FRAME
        self.canvas_frame = tk.Frame(master=root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
            
        ## PLOT FRAME
        self.plot_frame = tk.Frame(master=self.canvas_frame)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = FigureCanvasTkAgg(self.colreg_plot.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # TOOLBAR FRAME
        self.toolbar_frame = tk.Frame(master=root, height=50)
        self.toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.toolbar_frame.pack_propagate(False)
        ## SLIDERS
        self.real_time_slider = self.create_slider('Real time:', 10, TWO_HOURS * 4, ANIM_REAL_TIME, 10, self.update_anim_real_time)
        self.sim_time_slider = self.create_slider('Sim time:', 10, TWO_MINUTES, ANIM_SIM_TIME, 10, self.update_anim_sim_time)
        ## TOOLBAR
        toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        toolbar.update()
        toolbar.pack(fill=tk.BOTH, side=tk.LEFT)
        
        
        ## CONTROL FRAME
        self.control_frame = tk.Frame(master=self.canvas_frame)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ### TIME CONTROL
        self.time_control_frame = tk.Frame(self.control_frame, background='white')
        self.time_control_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.time_label = tk.Label(master=self.time_control_frame,
                              text=self.colreg_plot.animation.get_sim_time_count(), background='white', width=30)
        self.time_label.pack(side=tk.TOP, anchor='w', fill=tk.NONE)
        self.update_sim_time()
        
        #### LEGEND CHECKBOX
        self.legend_frame = tk.Frame(self.control_frame)
        self.legend_frame.pack(side=tk.TOP, fill=tk.NONE, expand=True)
        StandaloneCheckbox(self.legend_frame, 
                           self.colreg_plot.legend_component.graphs, 'white', False,
                           canvas = self.canvas, text='Legend')
        
        ### ACTOR CONTROL
        self.actor_control_frame = tk.Frame(self.control_frame)
        self.actor_control_frame.pack(side=tk.TOP, fill=tk.NONE, pady=(10, 0), expand=True)
        
        #### ACTOR CHECKBOXES        
        self.actor_columns : List[tk.Misc] = []
        col=self.create_actor_col('grey')
        actors_label = tk.Label(master=col, text='Component', background='grey')
        actors_label.pack(side=tk.TOP, fill=tk.NONE, pady=(0, 5))
        for vessel in env.vessels:
            col = self.create_actor_col(light_colors[vessel.id])
            actors_label = tk.Label(master=col, text=vessel.name, background=light_colors[vessel.id])
            actors_label.pack(side=tk.TOP, fill=tk.NONE, pady=(0, 5))
        
        self.create_actor_checkbox_row([self.colreg_plot.ship_markings_component.ship_dot_graphs], 'Dot')
        self.create_actor_checkbox_row([self.colreg_plot.ship_markings_component.velocity_graphs], 'Velocity')
        self.create_actor_checkbox_row([self.colreg_plot.ship_markings_component.radius_graphs], 'Radius')
        self.create_actor_checkbox_row([self.colreg_plot.ship_image_component.ship_image_graphs], 'Image')
        self.create_actor_checkbox_row([self.colreg_plot.ship_image_component.traj_line_graphs], 'Traj')
        self.create_actor_checkbox_row(self.colreg_plot.angle_circle_component.graphs_by_vessel, 'c')
        self.create_actor_checkbox_row(self.colreg_plot.centered_angle_circle_component.graphs_by_vessel, 'C', False)
        
        ### COLREG CONTROL
        self.colreg_control_frame = tk.Frame(self.control_frame)
        self.colreg_control_frame.pack(side=tk.TOP, fill=tk.NONE, pady=(10, 0), expand=True)
        
        #### CORLEG CHECKBOXES
        self.colreg_columns : List[tk.Misc] = []
        col=self.create_colreg_col('grey')
        colregs_label = tk.Label(master=col, text='Component', background='grey')
        colregs_label.pack(side=tk.TOP, fill=tk.NONE, pady=(0, 5))
        self.colregs_sorted = sorted(self.env.colreg_situations, key=lambda colreg_s: colreg_s.name)
        for colreg_s in self.colregs_sorted:
            col = self.create_colreg_col(light_colors[colreg_s.vessel1.id])
            colregs_label = tk.Label(master=col, text=colreg_s.short_name, background=light_colors[colreg_s.vessel1.id])
            colregs_label.pack(side=tk.TOP, fill=tk.NONE, pady=(0, 5))
            
        self.create_colreg_checkbox_row(self.sort_dict(self.colreg_plot.distance_component.graphs_by_colregs), 'Dist', True)
        self.create_colreg_checkbox_row(self.sort_dict(self.colreg_plot.vo_cone_component.graphs_by_colregs), 'VO cone', False)
        self.create_colreg_checkbox_row(self.sort_dict(self.colreg_plot.add_vo_cone_component.graphs_by_colregs), 'VO calc', False)
        self.create_colreg_checkbox_row(self.sort_dict([self.colreg_plot.prime_component.p12_vec_graphs]), 'P12', False)
        self.create_colreg_checkbox_row(self.sort_dict([self.colreg_plot.prime_component.p21_vec_graphs]), 'P21', False)
        
        
        root.mainloop()
        
    def create_actor_checkbox_row(self, plot_components: List[List[plt.Artist]], text: str, init_checked=True):
        for pc in plot_components:
            if len(self.actor_columns) != len(pc) + 1:
                raise Exception('data and column dimensions do not match!')
        
        cb_array = CheckboxArray(self.actor_columns[0], text, self.canvas)
        actor_columns = self.actor_columns[1:]
        for o in self.env.vessels:
            Checkbox(actor_columns[o.id], [cp[o.id] for cp in plot_components], cb_array, light_colors[o.id], init_checked)
            
            
    def create_colreg_checkbox_row(self, plot_components: List[List[plt.Artist]], text: str, init_checked=True):
        for pc in plot_components:
            if len(self.colreg_columns) != len(pc) + 1:
                raise Exception('data and column dimensions do not match!')
        
        cb_array = CheckboxArray(self.colreg_columns[0], text, self.canvas)
        colreg_columns = self.colreg_columns[1:]
        for i, colreg_s in enumerate(self.colregs_sorted):
            Checkbox(colreg_columns[i], [cp[i] for cp in plot_components], cb_array,
                     light_colors[colreg_s.vessel2.id], init_checked)
        
    def create_actor_col(self, color):
        col = tk.Frame(self.actor_control_frame, background=color)
        col.pack(side=tk.LEFT, fill=tk.NONE, expand=True)
        self.actor_columns.append(col)
        return col
    
    def create_colreg_col(self, color):
        col = tk.Frame(self.colreg_control_frame, background=color)
        col.pack(side=tk.LEFT, fill=tk.NONE, expand=True)
        self.colreg_columns.append(col)
        return col
    
    def create_slider(self, label, min_val, max_val, init_val, step_value, command):
        label = tk.Label(self.toolbar_frame, text=label)
        label.pack(side=tk.LEFT)
        
        slider = tk.Scale(self.toolbar_frame, from_=min_val, to=max_val, orient='horizontal', resolution=step_value,
                          command=command)
        slider.set(init_val)
        slider.pack(fill=tk.BOTH, side=tk.LEFT)
        return slider
    
    def update_anim_real_time(self, event):
        self.colreg_plot.animation.real_time_value = self.real_time_slider.get()
        
    def update_anim_sim_time(self, event):
        self.colreg_plot.animation.sim_time_value = self.sim_time_slider.get()
        
    def update_sim_time(self):
        # Fetch new data
        self.colreg_plot.animation.get_sim_time_count()
        self.time_label.config(text=self.colreg_plot.animation.get_sim_time_count())
        # Schedule the next update
        self.time_label.after(1000, self.update_sim_time) 
        
    def sort_dict(self, dicts : List[Dict[str, plt.Artist]]) -> List[List[plt.Artist]]:
        artists = []
        for dict in dicts:
            artists.append([value for key, value in sorted(dict.items())])
        return artists



