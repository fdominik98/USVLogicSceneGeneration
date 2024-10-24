from typing import Dict, List
from model.vessel import Vessel
from model.relation import Relation


class VesselNode():
    def __init__(self, vessel: Vessel) -> None:
        self.vessel = vessel
        self.relations : List[Relation] = []  
        self.in_degree = 0
        self.out_degree = 0      
    
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselNode) and
            self.vessel.id == value.vessel.id)
        
    def __repr__(self) -> str:
        return self.vessel.name

        
class VesselOrderGraph():
    def __init__(self, relations : List[Relation]):
        self.nodes : Dict[int, VesselNode] = {}
        self.in_degree : Dict[VesselNode, int] = {}
        self.out_degree : Dict[VesselNode, int] = {}
        
        for rel in relations:
            self.add_nodes(rel)
        for rel in relations:
            self.add_edge(rel)
            
    def add_nodes(self, rel : Relation):
        node1 = VesselNode(rel.vessel1)
        if rel.vessel1.id not in self.nodes:
            self.nodes[rel.vessel1.id] = node1
        node2 = VesselNode(rel.vessel2)
        if rel.vessel2.id not in self.nodes:
            self.nodes[rel.vessel2.id] = node2

    def add_edge(self, rel : Relation):
        if not rel.no_colreg():
            return
        node1 = self.nodes[rel.vessel1.id]
        node2 = self.nodes[rel.vessel2.id]
        node1.relations.append(rel)
        node1.out_degree += 1
        node2.in_degree += 1
        if rel.has_head_on():
            node2.relations.append(rel)
            node2.out_degree += 1
            node1.in_degree += 1
            
            
    def sort(self)-> list[VesselNode]:
        return sorted(self.nodes.values(), key=lambda node: node.out_degree - node.in_degree)