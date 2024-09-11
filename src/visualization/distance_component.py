from typing import Dict, List
from matplotlib import pyplot as plt
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent, light_colors
from model.usv_config import N_MILE_TO_M_CONVERSION


class DistanceComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)
        self.text_graphs : Dict[str, plt.Text] = {}
        self.line_graphs : Dict[str, plt.Line2D] = {}
        self.zorder = -3
            
    def do_draw(self):
        for colreg_s in self.env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2    
            
            text_str = f'{colreg_s.o_distance / N_MILE_TO_M_CONVERSION:.1f} NM'
            text = self.ax.text(o1.p[0] + colreg_s.p12[0] / 2, o1.p[1] + colreg_s.p12[1] / 2, text_str, fontsize=10, color='grey', zorder=self.zorder + 10)
            self.text_graphs[colreg_s.name] = text
            
            line, = self.ax.plot([o1.p[0], o2.p[0]], [o1.p[1], o2.p[1]], color=light_colors[5], linewidth=0.8, zorder=self.zorder)
            self.line_graphs[colreg_s.name] = line
            
            self.graphs += [text, line]
        
    def do_update(self, new_env : USVEnvironment) -> List[plt.Artist]:
        for colreg_s in new_env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2   
            
            self.text_graphs[colreg_s.name].set_position((o1.p[0] + colreg_s.p12[0] / 2, o1.p[1] + colreg_s.p12[1] / 2))
            text_str = f'{colreg_s.o_distance / N_MILE_TO_M_CONVERSION:.1f} NM'
            self.text_graphs[colreg_s.name].set_text(text_str)
            
            self.line_graphs[colreg_s.name].set_data([o1.p[0], o2.p[0]], [o1.p[1], o2.p[1]])
        return self.graphs 