from matplotlib import pyplot as plt
from model.usv_environment import USVEnvironment
from visualization.plot_component import PlotComponent, light_colors
from model.usv_config import N_MILE_TO_M_CONVERSION


class PrimeComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, initial_visibility : bool, env : USVEnvironment) -> None:
        super().__init__(ax, initial_visibility, env)
        self.secondary_visibility = False
            
    def do_draw(self, zorder : int):
        for colreg_s in self.env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2    
            
            p12_scaled = colreg_s.p12 * 0.95
            p21_scaled = colreg_s.p21 * 0.95
            self.p12_vec = self.ax.quiver(o1.p[0], o1.p[1], p12_scaled[0], p12_scaled[1], angles='xy', scale_units='xy', scale=1, color='black', zorder=zorder-10)
            self.p21_vec = self.ax.quiver(o2.p[0], o2.p[1], p21_scaled[0], p21_scaled[1], angles='xy', scale_units='xy', scale=1, color='black', zorder=zorder-10)
            self.p12_vec.set_visible(self.visible)
            self.p21_vec.set_visible(self.secondary_visibility)
    
    def toggle(self):
        if self.visible:
            self.visible = False
            self.secondary_visibility = True
        elif self.secondary_visibility:
            self.visible = self.secondary_visibility = False
        else:
            self.visible = True
        self.p12_vec.set_visible(self.visible)
        self.p21_vec.set_visible(self.secondary_visibility)
        