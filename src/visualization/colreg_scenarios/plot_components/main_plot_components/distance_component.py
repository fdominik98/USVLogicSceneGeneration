from typing import Dict, List
from matplotlib import pyplot as plt
from logical_level.models.logical_scenario import LogicalScenario
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent
from asv_utils import N_MILE_TO_M_CONVERSION


class DistanceComponent(PlotComponent):
    def __init__(self, ax: plt.Axes,logical_scenario: LogicalScenario) -> None:
        super().__init__(ax, env)
        self.text_graphs : Dict[str, plt.Text] = {}
        self.line_graphs : Dict[str, plt.Line2D] = {}
        self.graphs_by_rels = [self.text_graphs, self.line_graphs]
        self.zorder = -3
            
    def do_draw(self):
        for rel in self.logical_scenario.relations:
            o1 = rel.vessel1
            o2 = rel.vessel2    
            
            text_str = f'{rel.o_distance / N_MILE_TO_M_CONVERSION:.1f} NM'
            text = self.ax.text(o1.p[0] + rel.p12[0] / 2, o1.p[1] + rel.p12[1] / 2, text_str, fontsize=10, color='black', zorder=self.zorder + 10)
            self.text_graphs[rel.name] = text
            
            line, = self.ax.plot([o1.p[0], o2.p[0]], [o1.p[1], o2.p[1]], color='black', linewidth=0.8, zorder=self.zorder)
            self.line_graphs[rel.name] = line
            
            self.graphs += [text, line]
        
    def do_update(self, new_env : LogicalScenario) -> List[plt.Artist]:
        for rel in new_env.relations:
            o1 = rel.vessel1
            o2 = rel.vessel2   
            
            self.text_graphs[rel.name].set_position((o1.p[0] + rel.p12[0] / 2, o1.p[1] + rel.p12[1] / 2))
            text_str = f'{rel.o_distance / N_MILE_TO_M_CONVERSION:.1f} NM'
            self.text_graphs[rel.name].set_text(text_str)
            
            self.line_graphs[rel.name].set_data([o1.p[0], o2.p[0]], [o1.p[1], o2.p[1]])
        return self.graphs 