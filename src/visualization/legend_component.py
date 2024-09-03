from typing import List
from matplotlib import pyplot as plt
from matplotlib.legend import Legend
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent

class LegendComponent(PlotComponent):
    
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)

    def do_draw(self, zorder : int):
        self.legend = self.create_legend()
        self.graphs += [self.legend]
        
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        self.graphs.remove(self.legend)
        self.legend.remove()
        self.legend = self.create_legend()
        self.graphs += [self.legend]
        return self.graphs
    
    def create_legend(self) -> Legend:
        return self.ax.legend()
    