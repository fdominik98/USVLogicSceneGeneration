from typing import Dict, List
from model.colreg_situation import ColregSituation, HeadOn, NoColreg
from model.vessel import Vessel


class VesselNode():
    def __init__(self, vessel: Vessel) -> None:
        self.vessel = vessel
        self.colreg_situations : List[ColregSituation] = []  
        self.in_degree = 0
        self.out_degree = 0      
    
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselNode) and
            self.vessel.id == value.vessel.id)
        
    def __repr__(self) -> str:
        return self.vessel.name

        
class VesselOrderGraph():
    def __init__(self, colreg_situations : List[ColregSituation]):
        self.nodes : Dict[int, VesselNode] = {}
        self.in_degree : Dict[VesselNode, int] = {}
        self.out_degree : Dict[VesselNode, int] = {}
        
        for colreg_s in colreg_situations:
            self.add_nodes(colreg_s)
        for colreg_s in colreg_situations:
            self.add_edge(colreg_s)
            
    def add_nodes(self, colreg_s : ColregSituation):
        node1 = VesselNode(colreg_s.vessel1)
        if colreg_s.vessel1.id not in self.nodes:
            self.nodes[colreg_s.vessel1.id] = node1
        node2 = VesselNode(colreg_s.vessel2)
        if colreg_s.vessel2.id not in self.nodes:
            self.nodes[colreg_s.vessel2.id] = node2

    def add_edge(self, colreg_s : ColregSituation):
        if isinstance(colreg_s, NoColreg):
            return
        node1 = self.nodes[colreg_s.vessel1.id]
        node2 = self.nodes[colreg_s.vessel2.id]
        node1.colreg_situations.append(colreg_s)
        node1.out_degree += 1
        node2.in_degree += 1
        if isinstance(colreg_s, HeadOn):
            node2.colreg_situations.append(colreg_s)
            node2.out_degree += 1
            node1.in_degree += 1
            
            
    def sort(self)-> list[VesselNode]:
        return sorted(self.nodes.values(), key=lambda node: node.out_degree - node.in_degree)