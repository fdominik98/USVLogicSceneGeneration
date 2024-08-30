from matplotlib import pyplot as plt
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent, light_colors
from model.usv_config import N_MILE_TO_M_CONVERSION


class PrimeComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)
        self.secondary_visibility = False
        self.p12_vec_graphs : dict[str, plt.Quiver] = {}
        self.p21_vec_graphs : dict[str, plt.Quiver] = {}
            
    def do_draw(self, zorder : int):
        for colreg_s in self.env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2    
            
            p12_scaled = colreg_s.p12 * 0.95
            p12_vec = self.ax.quiver(o1.p[0], o1.p[1], p12_scaled[0], p12_scaled[1], angles='xy', scale_units='xy', scale=1, color='black', zorder=zorder-10)
            self.p12_vec_graphs[colreg_s.name] = p12_vec
            
            p21_scaled = colreg_s.p21 * 0.95
            p21_vec = self.ax.quiver(o2.p[0], o2.p[1], p21_scaled[0], p21_scaled[1], angles='xy', scale_units='xy', scale=1, color='black', zorder=zorder-10)
            self.p21_vec_graphs[colreg_s.name] = p21_vec
            
            self.graphs += [p12_vec, p21_vec]
            self.refresh_visible()
    
    def toggle(self):
        if self.visible:
            self.visible = False
            self.secondary_visibility = True
        elif self.secondary_visibility:
            self.visible = self.secondary_visibility = False
        else:
            self.visible = True
        self.refresh_visible()
    
    def refresh_visible(self):        
        for g in self.p12_vec_graphs.values():
            g.set_visible(self.visible)
        for g in self.p21_vec_graphs.values():
            g.set_visible(self.secondary_visibility)
        
    def update(self, new_env : USVEnvironment) -> list[plt.Artist]:
        for colreg_s in new_env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2
            
            p12_scaled = colreg_s.p12 * 0.95
            self.p12_vec_graphs[colreg_s.name].set_offsets(o1.p)
            self.p12_vec_graphs[colreg_s.name].set_UVC(p12_scaled[0], p12_scaled[1])
            p21_scaled = colreg_s.p21 * 0.95
            self.p21_vec_graphs[colreg_s.name].set_offsets(o2.p)
            self.p21_vec_graphs[colreg_s.name].set_UVC(p21_scaled[0], p21_scaled[1])
        return self.graphs