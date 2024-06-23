import networkx as nx
from model.colreg_situation_config import ColregSituationConfig
from model.usv_config import *
from model.vessel import Vessel
from model.colreg_situation import ColregSituation, NoColision, NoConstraint
from networkx.algorithms import isomorphism
import math

class InstanceInitializer():
    def __init__(self, radii : list[float], colreg_situation_configs : list[ColregSituationConfig]) -> None:
        self.radii = radii
        self.colreg_situation_configs = colreg_situation_configs
        sorted_radii = sorted(self.radii, reverse=True)
        
        min_cell_size = sorted_radii[0] + sorted_radii[1]
        min_cell_size = max_distance / 9
        self.min_r = sorted_radii[-1]
        
        colreg_classes : dict[ColregSituation.__class__, float] = dict()
        for colreg_situation in colreg_situation_configs:
            if colreg_situation.colreg_class == NoColision or colreg_situation.colreg_class == NoConstraint:
                continue
            if colreg_situation.colreg_class in colreg_classes:
                lower_bound = colreg_classes[colreg_situation.colreg_class][0]
                colreg_classes[colreg_situation.colreg_class] = None if colreg_situation.distance is None else [min(colreg_situation.distance[0], lower_bound), max_distance]
            else:
                colreg_classes[colreg_situation.colreg_class] = None if colreg_situation.distance is None else (colreg_situation.distance[0], max_distance)
                   
        self.node_id = 0
        
        G = nx.Graph()
        
        x = point_min + min_cell_size
        
        average_speed = (speed_max - speed_min) / 2
        
        while x < point_max:
            y = point_min + min_cell_size
            while y < point_max:
                self.generate_node(G, (x, y), (average_speed, 0))
                self.generate_node(G, (x, y), (-average_speed, 0))
                self.generate_node(G, (x, y), (0, average_speed))
                self.generate_node(G, (x, y), (0, -average_speed))
                y += min_cell_size
            x+= min_cell_size
            
        for node1 in G.nodes:
            for node2 in G.nodes:
                if node1 == node2:
                    continue
                vessel1 = G.nodes[node1]['attribute']
                vessel2 = G.nodes[node2]['attribute']
                for colreg_class in colreg_classes.keys():
                    colreg_situation = colreg_class(distance=colreg_classes[colreg_class], vessel1=vessel1, vessel2=vessel2)
                    if colreg_situation.penalties[0] + colreg_situation.penalties[3] + colreg_situation.penalties[2] == 0.0:
                        G.add_edge(node1, node2, label=colreg_class)
                
                
        P = nx.Graph()
        
        for i, _ in enumerate(self.radii):
            P.add_node(i)
            
        for colreg_situation in colreg_situation_configs:
            if colreg_situation.colreg_class == NoColision or colreg_situation.colreg_class == NoConstraint:
                continue
            P.add_edge(colreg_situation.id1, colreg_situation.id2, label=colreg_situation.colreg_class)
            
        self.GM = isomorphism.GraphMatcher(G, P, edge_match=self.edge_match)             
                
                
    def get_population(self, num : int) -> list[tuple[list[Vessel], set[ColregSituation]]]:
        result : list[tuple[list[Vessel], set[ColregSituation]]] = []
        for subgraph in self.get_limited_matches(self.GM, num):
            vessels : list[Vessel] = []
            for G_node in subgraph.keys():
                G_vessel : Vessel = self.GM.G1.nodes[G_node]['attribute']
                vessel = Vessel(subgraph[G_node], self.radii[subgraph[G_node]])
                vessel.update(G_vessel.p[0], G_vessel.p[1], G_vessel.v[0], G_vessel.v[1])
                vessels.append(vessel)
                
            colreg_situations : set[ColregSituation] = set()        
            for colreg_situation in self.colreg_situation_configs:
                colreg_situations.add(colreg_situation.colreg_class(vessels[colreg_situation.id1],
                                                                vessels[colreg_situation.id2], colreg_situation.distance)) 
            result.append((vessels, colreg_situations))
        return result
        
        
                
    def generate_node(self, G : nx.Graph, p, v):
        vessel = Vessel(id=-1, r=self.min_r)
        vessel.update(p[0], p[1], v[0], v[1])
        G.add_node(self.node_id, attribute=vessel)
        self.node_id += 1
        
    def edge_match(self, e1, e2):
        return e1['label'] == e2['label']
    
    def get_limited_matches(self, GM : isomorphism.GraphMatcher, limit) -> list[dict]:
        matches = []
        count = 0
        for subgraph in GM.subgraph_isomorphisms_iter():
            if self.has_unique_positions(GM.G1, subgraph):
                matches.append(subgraph)
                count += 1
                if count >= limit:
                    break
        if count < limit:
            matches = (matches * math.ceil(limit/count))[:limit]
        return matches
    
    def has_unique_positions(self, G: nx.Graph, d : dict):
        remainders = {tuple(G.nodes[key]['attribute'].p.flatten()) for key in d.keys()}
        return len(remainders) == len(d.keys())
