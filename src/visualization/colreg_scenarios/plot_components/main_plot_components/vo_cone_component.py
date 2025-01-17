from typing import Dict, List, Tuple
from matplotlib import pyplot as plt
import numpy as np
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache
from visualization.colreg_scenarios.plot_components.plot_component import PlotComponent, colors


class VOConeComponent(PlotComponent):
    def __init__(self, ax : plt.Axes, scenario : MultiLevelScenario) -> None:
        super().__init__(ax, scenario)
        self.other_velocity_graphs : Dict[Tuple[ConcreteVessel, ConcreteVessel], plt.Quiver] = {}
        self.line1_graphs : Dict[Tuple[ConcreteVessel, ConcreteVessel], plt.Line2D] = {}
        self.line2_graphs : Dict[Tuple[ConcreteVessel, ConcreteVessel], plt.Line2D] = {}
        self.filling_graphs : Dict[Tuple[ConcreteVessel, ConcreteVessel], plt.Polygon] = {}
        self.graphs_by_rels = [self.other_velocity_graphs, self.line1_graphs, self.line2_graphs, self.filling_graphs]
        self.zorder = -1
            
    def do_draw(self):
        eval_cache = EvaluationCache(self.scenario.concrete_scene.assignments(self.scenario.logical_scenario.actor_vars))
        for vessel1, vessel2 in self.scenario.concrete_scene.all_actor_pairs:
            var1, var2 = self.scenario.to_variable(vessel1), self.scenario.to_variable(vessel2)
            key = (vessel1, vessel2)
            props = eval_cache.get_props(var1, var2)
            # Calculate the angles of the cone
            angle_rel = np.arctan2(props.p12[1], props.p12[0])
            sin_half_cone_theta = np.clip(props.safety_dist / props.o_distance, -1, 1)
            angle_half_cone = abs(np.arcsin(sin_half_cone_theta)) # [0, pi/2] 
            angle1 = angle_rel + angle_half_cone
            angle2 = angle_rel - angle_half_cone
            
            cone_size = max(props.o_distance / 2, (props.val1.sp + props.val2.sp) * 1.2)
                        
            cone1 = props.val2.v + props.val1.p + np.array([np.cos(angle1), np.sin(angle1)]) * cone_size
            cone2 = props.val2.v + props.val1.p + np.array([np.cos(angle2), np.sin(angle2)]) * cone_size
        
            line1, = self.ax.plot([props.val2.v[0] + props.val1.x, cone1[0]], [props.val2.v[1] + props.val1.y, cone1[1]], '--', color=colors[vessel2.id], linewidth=0.7, zorder=self.zorder)
            line2, = self.ax.plot([props.val2.v[0] + props.val1.x, cone2[0]], [props.val2.v[1] + props.val1.y, cone2[1]], '--', color=colors[vessel2.id], linewidth=0.7, zorder=self.zorder)
            self.line1_graphs[key] = line1
            self.line2_graphs[key] = line2
        
            # Move the other vessels velocity vector in the o1 position to see if the vector is in the VO cone  
            other_velocity = self.ax.quiver(props.val1.x, props.val1.y, props.val2.v[0], props.val2.v[1], angles='xy', scale_units='xy', scale=1, color=colors[vessel2.id], zorder=self.zorder-10)
            self.other_velocity_graphs[key] = other_velocity
            
            # Fill the cone with a semi-transparent color
            filling = self.ax.fill([props.val2.v[0] + props.val1.x, cone1[0], cone2[0]],
                        [props.val2.v[1] + props.val1.y, cone1[1], cone2[1]],
                        color=colors[vessel2.id], alpha=0.15, zorder=self.zorder)
            self.filling_graphs[key] = filling[0]
            
            self.graphs += [line1, line2, other_velocity, filling[0]] 
        
    def do_update(self, scene : ConcreteScene) -> List[plt.Artist]:
        eval_cache = EvaluationCache(scene.assignments(self.scenario.logical_scenario.actor_vars))
        for vessel1, vessel2 in self.other_velocity_graphs.keys():
            var1, var2 = self.scenario.to_variable(vessel1), self.scenario.to_variable(vessel2)
            key = (vessel1, vessel2)
            props = eval_cache.get_props(var1, var2)
            # Calculate the angles of the cone
            angle_rel = np.arctan2(props.p12[1], props.p12[0])
            # Calculate the angles of the cone
            angle_rel = np.arctan2(props.p12[1], props.p12[0])
            sin_half_cone_theta = np.clip(props.safety_dist / props.o_distance, -1, 1)
            angle_half_cone = abs(np.arcsin(sin_half_cone_theta)) # [0, pi/2] 
            angle1 = angle_rel + angle_half_cone
            angle2 = angle_rel - angle_half_cone
            
            cone_size = max(props.o_distance / 2, (props.val1.sp + props.val2.sp) * 1.2)
                        
            cone1 = props.val2.v + props.val1.p + np.array([np.cos(angle1), np.sin(angle1)]) * cone_size
            cone2 = props.val2.v + props.val1.p + np.array([np.cos(angle2), np.sin(angle2)]) * cone_size
            self.line1_graphs[key].set_data([props.val2.v[0] + props.val1.x, cone1[0]], [props.val2.v[1] + props.val1.y, cone1[1]])
            self.line2_graphs[key].set_data([props.val2.v[0] + props.val1.x, cone2[0]], [props.val2.v[1] + props.val1.y, cone2[1]])
            self.other_velocity_graphs[key].set_offsets(props.val1.p)
            self.other_velocity_graphs[key].set_UVC(props.val2.v[0], props.val2.v[1])
            
            polx = [props.val2.v[0] + props.val1.x, cone1[0], cone2[0]]
            poly = [props.val2.v[1] + props.val1.y, cone1[1], cone2[1]]
            self.filling_graphs[key].set_xy(np.array([polx, poly]).T)
        return self.graphs