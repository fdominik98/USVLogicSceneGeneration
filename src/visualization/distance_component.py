from matplotlib import pyplot as plt
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent, light_colors


class DistanceComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)
            
    def do_draw(self, zorder : int):
        for colreg_s in self.env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2    
            
            text = self.ax.text(o1.p[0] + colreg_s.p12[0] / 2, o1.p[1] + colreg_s.p12[1] / 2, f'{colreg_s.o_distance:.2f} m', fontsize=10, color='grey', zorder=zorder + 10)
            line, = self.ax.plot([o1.p[0], o2.p[0]], [o1.p[1], o2.p[1]], color=light_colors[5], linewidth=0.8, zorder=zorder)
            self.graphs += [text, line]
        