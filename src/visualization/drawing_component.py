from typing import Dict, List
from matplotlib import pyplot as plt
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent, light_colors
from model.usv_config import N_MILE_TO_M_CONVERSION


class DrawingComponent(PlotComponent):
    def __init__(self, fig : plt.Figure, ax: plt.Axes, env : USVEnvironment) -> None:
        super().__init__(ax, env)
        self.fig = fig
        self.draw_x : List[List[float]] = []
        self.draw_y : List[List[float]] = []
            
    def do_draw(self):
        pass
        
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        return self.graphs 
    
    # Function to handle mouse clicks
    def on_click(self, event):
        if self.fig.canvas.toolbar.mode:
            return
        if event.button == 1:  # Left mouse button
            self.draw_x.append([event.xdata])
            self.draw_y.append([event.ydata])
            (line, ) = self.ax.plot(self.draw_x[-1], self.draw_y[-1], 'g:', lw=2)
            self.graphs.append(line)  # Draw a line connecting the points
            self.fig.canvas.draw()
        if event.button == 3:
            if len(self.graphs) == 0:
                return
            self.draw_x = self.draw_x[:-1]
            self.draw_y = self.draw_y[:-1]
            self.graphs[-1].remove()
            self.graphs = self.graphs[:-1]
            self.fig.canvas.draw()

    # Function to handle mouse movements
    def on_move(self, event):
        if self.fig.canvas.toolbar.mode:
            return
        if event.button == 1 and event.xdata is not None and event.ydata is not None:
            self.draw_x[-1].append(event.xdata)
            self.draw_y[-1].append(event.ydata)
            self.graphs[-1].set_data(self.draw_x[-1], self.draw_y[-1])
            self.fig.canvas.draw()