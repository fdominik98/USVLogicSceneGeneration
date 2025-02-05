from typing import Dict, List, Tuple
from functional_level.metamodels.functional_object import FuncObject
from functional_level.metamodels.functional_scenario import FunctionalScenario

class VesselNode():
    def __init__(self, vessel: FuncObject) -> None:
        self.vessel = vessel
        self.relations : List[Tuple[FuncObject, FuncObject]] = []  
        self.in_degree = 0
        self.out_degree = 0      
    
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselNode) and
            self.vessel.id == value.vessel.id)
        
    def __repr__(self) -> str:
        return self.vessel.__repr__()

        
class VesselOrderGraph():
    def __init__(self, functional_scenario : FunctionalScenario):
        self.nodes : Dict[int, VesselNode] = {}
        self.in_degree : Dict[VesselNode, int] = {}
        self.out_degree : Dict[VesselNode, int] = {}
        
        relations = functional_scenario.binary_interpretation_tuples
        
        for rel in relations:
            self.add_nodes(rel)
        for rel in relations:
            self.add_edge(rel)
            
    def add_nodes(self, rel : Tuple[FuncObject, FuncObject]):
        node1 = VesselNode(rel[0])
        if rel[0] not in self.nodes:
            self.nodes[rel[0]] = node1
        node2 = VesselNode(rel[1])
        if rel[1] not in self.nodes:
            self.nodes[rel[1]] = node2

    def add_edge(self, rel : Tuple[FuncObject, FuncObject]):
        node1 = self.nodes[rel[0]]
        node2 = self.nodes[rel[1].id]
        node1.relations.append(rel)
        node1.out_degree += 1
        node2.in_degree += 1
            
            
    def sort(self)-> list[VesselNode]:
        return sorted(self.nodes.values(), key=lambda node: node.out_degree - node.in_degree)