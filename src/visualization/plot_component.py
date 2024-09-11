from typing import List
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
        self.graphs : List[plt.Artist] = []
        self.zorder = 0
        
    def draw(self):
        self.do_draw()
        self.refresh_visible()
        
        
    def toggle(self):
        self.visible = not self.visible
        self.refresh_visible()
        
        
    def refresh_visible(self):
        for g in self.graphs:
            g.set_visible(self.visible)
          
    @abstractmethod  
    def do_draw(self):
        pass
    
    def update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        if self.visible:
            return self.do_update(new_env)      
        return []  
    
    @abstractmethod
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        pass        
    
    def reset(self) -> List[plt.Artist]:
        return self.update(self.env)