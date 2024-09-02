from matplotlib import pyplot as plt
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent

class LegendComponent(PlotComponent):
    
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)

    def do_draw(self, zorder : int):
        self.legend = self.ax.legend(loc=7)
        self.graphs = [self.legend]
        
    def do_update(self, new_env : USVEnvironment) -> list[plt.Artist]:
        self.legend.remove()
        self.legend = self.ax.legend(loc=7)
        self.graphs = [self.legend]
        return self.graphs
    
    