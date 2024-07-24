from model.colreg_situation_config import ColregSituationConfig
from model.usv_config import max_distance, point_max, point_min, speed_max, speed_min
from model.vessel import Vessel
from model.colreg_situation import ColregSituation, NoColreg
import math
from igraph import Graph

class InstanceInitializer():
    def __init__(self, radii : list[float], colreg_situation_configs : list[ColregSituationConfig]) -> None:
        self.radii = radii
        self.actor_num = len(radii)
        self.colreg_situation_configs = colreg_situation_configs
        sorted_radii = sorted(self.radii, reverse=True)
        self.max_distance = max_distance(self.actor_num)
        
        min_cell_size = sorted_radii[0] + sorted_radii[1]
        min_cell_size = self.max_distance / 8
        self.min_r = sorted_radii[-1]
        
        colreg_classes_dist : dict[ColregSituation.__class__, float] = dict()
        colreg_classes_id : list[ColregSituation.__class__] = []
        
        for colreg_situation in colreg_situation_configs:
            colreg_class = colreg_situation.colreg_class
            if colreg_class == NoColreg:
                continue
            if colreg_class in colreg_classes_dist:
                lower_bound = colreg_classes_dist[colreg_class][0]
                colreg_classes_dist[colreg_class] = None if colreg_situation.distance is None else [min(colreg_situation.distance[0], lower_bound), self.max_distance]
            else:
                colreg_classes_dist[colreg_class] = None if colreg_situation.distance is None else (colreg_situation.distance[0], self.max_distance)
                colreg_classes_id.append(colreg_class)
                   
        self.node_id = 0
        self.G = Graph(directed=True)
        
        x = point_min + min_cell_size
        
        average_speed = (speed_max - speed_min) / 2
        
        while x < point_max(self.actor_num):
            y = point_min + min_cell_size
            while y < point_max(self.actor_num):
                self.generate_node(self.G, (x, y), (average_speed, 0))
                self.generate_node(self.G, (x, y), (-average_speed, 0))
                self.generate_node(self.G, (x, y), (0, average_speed))
                self.generate_node(self.G, (x, y), (0, -average_speed))
                y += min_cell_size
            x+= min_cell_size
            
        for node1 in self.G.vs:
            for node2 in self.G.vs:
                if node1 == node2:
                    continue
                vessel1 = node1['attribute']
                vessel2 = node2['attribute']
                for colreg_class in colreg_classes_dist.keys():
                    colreg_situation = colreg_class(distance=colreg_classes_dist[colreg_class], vessel1=vessel1, vessel2=vessel2, max_distance=self.max_distance)
                    if colreg_situation.penalties[0] + colreg_situation.penalties[2] == 0.0:
                        self.G.add_edge(node1, node2, key=colreg_classes_id.index(colreg_class))
                
        self.P = Graph(directed=True)
        
        for i, _ in enumerate(self.radii):
            self.P.add_vertex(i)
            
        for colreg_situation in colreg_situation_configs:
            colreg_class = colreg_situation.colreg_class
            if colreg_class == NoColreg:
                continue
            self.P.add_edge(colreg_situation.id1, colreg_situation.id2, key=colreg_classes_id.index(colreg_class))
            
        # print(self.G.es["key"])
        # print(self.P.es["key"])        
                
                
    def get_population(self, num : int) -> list[tuple[list[Vessel], set[ColregSituation]]]:
        result : list[tuple[list[Vessel], set[ColregSituation]]] = []
        
        for subgraph in self.get_limited_matches(num):
            vessels : list[Vessel] = []
            for i, G_node in enumerate(subgraph):
                G_vessel : Vessel = self.G.vs[G_node]['attribute']
                vessel = Vessel(i, self.radii[i])
                vessel.update(G_vessel.p[0], G_vessel.p[1], G_vessel.v[0], G_vessel.v[1])
                vessels.append(vessel)
                
            vessels = sorted(vessels, key=lambda obj: obj.id)
                
            colreg_situations : set[ColregSituation] = set()        
            for colreg_situation in self.colreg_situation_configs:
                colreg_situations.add(colreg_situation.colreg_class(vessels[colreg_situation.id1],
                                                                vessels[colreg_situation.id2], colreg_situation.distance, self.max_distance)) 
            result.append((vessels, colreg_situations))
        return result       
                
    def generate_node(self, G : Graph, p, v):
        vessel = Vessel(id=-1, r=self.min_r)
        vessel.update(p[0], p[1], v[0], v[1])
        G.add_vertex(self.node_id, attribute=vessel)
        self.node_id += 1
        
    def get_limited_matches(self, limit) -> list[dict]:
        matches = []
        count = 0
        all_matches = self.G.get_subisomorphisms_vf2(self.P, edge_color1=self.G.es['key'], edge_color2=self.P.es['key'])
        for match in all_matches:
            if self.has_unique_positions(match):
                matches.append(match)
                count += 1
                if count >= limit:
                    break
        if count < limit:
            matches = (matches * math.ceil(limit/count))[:limit]
        return matches
    
    def has_unique_positions(self, match : list):
        remainders = {tuple(self.G.vs[node]['attribute'].p.flatten()) for node in match}
        return len(remainders) == len(match)
