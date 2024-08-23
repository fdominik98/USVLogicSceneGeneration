from matplotlib import pyplot as plt
import numpy as np
from model.usv_environment import USVEnvironment
from abc import ABC, abstractmethod

colors = ['blue', 'red', 'green', 'orange', 'purple', 'grey', 'olive']
light_colors = ['lightblue', 'salmon', 'lightgreen', 'moccasin', 'thistle', 'lightgrey', 'y']

class PlotComponent(ABC):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        self.ax = ax
        self.env = env
        self.visible = initial_visibility
        self.graphs : list[plt.Artist] = []
        
    def draw(self, zorder : int):
        self.do_draw(zorder)
        self.refresh_visible()
        
        
    def toggle(self):
        self.visible = not self.visible
        self.refresh_visible()
        
        
    def refresh_visible(self):
        for g in self.graphs:
            g.set_visible(self.visible)
          
    @abstractmethod  
    def do_draw(self, zorder : int):
        pass
        