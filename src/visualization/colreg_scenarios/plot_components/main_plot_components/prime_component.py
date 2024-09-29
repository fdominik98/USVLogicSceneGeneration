from typing import Dict, List
from matplotlib import pyplot as plt
from model.environment.usv_environment import USVEnvironment
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent


class PrimeComponent(PlotComponent):
    def __init__(self, ax: plt.Axes, env: USVEnvironment) -> None:
        super().__init__(ax, env)
        self.p12_vec_graphs: Dict[str, plt.Quiver] = {}
        self.p21_vec_graphs: Dict[str, plt.Quiver] = {}
        self.zorder = -15

    def do_draw(self):
        for colreg_s in self.env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2

            p12_scaled = colreg_s.p12 * 0.95
            p12_vec = self.ax.quiver(o1.p[0], o1.p[1], p12_scaled[0], p12_scaled[1],
                                     angles='xy', scale_units='xy', scale=1, color='black', zorder=self.zorder,
                                     width=0.006)
            self.p12_vec_graphs[colreg_s.name] = p12_vec

            p21_scaled = colreg_s.p21 * 0.95
            p21_vec = self.ax.quiver(o2.p[0], o2.p[1], p21_scaled[0], p21_scaled[1],
                                     angles='xy', scale_units='xy', scale=1, color='black', zorder=self.zorder,
                                     width=0.006)
            self.p21_vec_graphs[colreg_s.name] = p21_vec

            self.graphs += [p12_vec, p21_vec]

    def do_update(self, new_env: USVEnvironment) -> List[plt.Artist]:
        for colreg_s in new_env.colreg_situations:
            o1 = colreg_s.vessel1
            o2 = colreg_s.vessel2

            p12_scaled = colreg_s.p12 * 0.95
            self.p12_vec_graphs[colreg_s.name].set_offsets(o1.p)
            self.p12_vec_graphs[colreg_s.name].set_UVC(
                p12_scaled[0], p12_scaled[1])
            p21_scaled = colreg_s.p21 * 0.95
            self.p21_vec_graphs[colreg_s.name].set_offsets(o2.p)
            self.p21_vec_graphs[colreg_s.name].set_UVC(
                p21_scaled[0], p21_scaled[1])
        return self.graphs
