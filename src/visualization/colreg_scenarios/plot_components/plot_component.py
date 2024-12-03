from typing import List
from matplotlib import pyplot as plt
import numpy as np
from model.environment.usv_environment import LogicalScenario
from abc import ABC, abstractmethod

colors = ['blue', 'red', 'green', 'orange', 'purple', 'grey', 'olive']
light_colors = ['lightblue', 'salmon', 'lightgreen', 'moccasin', 'thistle', 'lightgrey', 'y']

class PlotComponent(ABC):
    def __init__(self, ax: plt.Axes, env : LogicalScenario) -> None:
        self.ax = ax
        self.env = env
        self.graphs : List[plt.Artist] = []
        self.zorder = 0
        
    def draw(self):
        self.do_draw()

          
    @abstractmethod  
    def do_draw(self):
        pass
    
    def update(self, new_env : LogicalScenario) -> List[plt.Artist]:
        return self.do_update(new_env)   
    
    @abstractmethod
    def do_update(self, new_env : LogicalScenario) -> List[plt.Artist]:
        pass        
    
    def reset(self) -> List[plt.Artist]:
        return self.update(self.env)