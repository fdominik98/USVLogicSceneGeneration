from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Optional, Set, Tuple
import copy
from functional_level.metamodels.functional_object import FuncObject
from functional_level.metamodels.interpretation import (
    BinaryInterpretation, HeadOnInterpretation, OvertakingInterpretation, CrossingFromPortInterpretation, OSInterpretation, TSInterpretation,
    VesselClass1Interpretation, VesselClass2Interpretation, VesselClass3Interpretation, VesselClass4Interpretation,
    VesselClass5Interpretation, VesselClass0Interpretation, VesselClass6Interpretation, VesselClass7Interpretation,
    VesselClass8Interpretation, VesselInterpretation)
from utils.scenario import Scenario
   
@dataclass(frozen=True)
class FunctionalScenario(Scenario):
    os_interpretation : OSInterpretation = OSInterpretation()
    ts_interpretation : TSInterpretation = TSInterpretation()
    head_on_interpretation : HeadOnInterpretation = HeadOnInterpretation()
    overtaking_interpretation : OvertakingInterpretation = OvertakingInterpretation()
    crossing_interpretation : CrossingFromPortInterpretation = CrossingFromPortInterpretation()
    
    vessel_class_0_interpretation : VesselClass0Interpretation = VesselClass0Interpretation()
    vessel_class_1_interpretation : VesselClass1Interpretation = VesselClass1Interpretation()
    vessel_class_2_interpretation : VesselClass2Interpretation = VesselClass2Interpretation()
    vessel_class_3_interpretation : VesselClass3Interpretation = VesselClass3Interpretation()
    vessel_class_4_interpretation : VesselClass4Interpretation = VesselClass4Interpretation()
    vessel_class_5_interpretation : VesselClass5Interpretation = VesselClass5Interpretation()
    vessel_class_6_interpretation : VesselClass6Interpretation = VesselClass6Interpretation()
    vessel_class_7_interpretation : VesselClass7Interpretation = VesselClass7Interpretation()
    vessel_class_8_interpretation : VesselClass8Interpretation = VesselClass8Interpretation()
    
    func_objects : List[FuncObject] = field(init=False)
    class_interpretation_list : List[VesselInterpretation] = field(init=False)
    
    def __post_init__(self):
        object_set : Set[FuncObject] = set()
        for interpretations in [self.os_interpretation, self.ts_interpretation, self.head_on_interpretation, self.overtaking_interpretation, self.crossing_interpretation]:
            for interpretation in interpretations:
                for func_object in interpretation:
                    object_set.add(func_object)
        object.__setattr__(self, 'func_objects', sorted(list(object_set), key=lambda x: x.id))
        head_on_interpretation_temp = copy.deepcopy(self.head_on_interpretation)
        for o1, o2 in head_on_interpretation_temp:
            self.head_on_interpretation.add(o1, o2)
            
        class_interpretation_list = [self.vessel_class_0_interpretation, self.vessel_class_1_interpretation,
                                    self.vessel_class_2_interpretation, self.vessel_class_3_interpretation,
                                    self.vessel_class_4_interpretation, self.vessel_class_5_interpretation,
                                    self.vessel_class_6_interpretation, self.vessel_class_7_interpretation,
                                    self.vessel_class_8_interpretation,
        ]
        object.__setattr__(self, 'class_interpretation_list', class_interpretation_list)
        
    
    @property
    def name(self):
        return f'{str(self.size)}vessel'
    
    def in_colreg_rel(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.colreg_rel(o1, o2) or self.colreg_rel(o2, o1)
    
    def in_overtaking(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.overtaking(o1, o2) or self.overtaking(o2, o1)
    
    def in_crossing(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.crossing(o1, o2) or self.crossing(o2, o1)
    
    def colreg_rel(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.head_on(o1, o2) or self.overtaking(o1, o2) or self.crossing(o1, o2)
    
    def head_on(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.head_on_interpretation.contains((o1, o2))
    
    def overtaking(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.overtaking_interpretation.contains((o1, o2))
    
    def crossing(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.crossing_interpretation.contains((o1, o2))
    
    def is_os(self, o : FuncObject) -> bool:
        return self.os_interpretation.contains(o)
    
    def is_ts(self, o : FuncObject) -> bool:
        return self.ts_interpretation.contains(o)
    
    def is_vessel_class_x(self, class_num : int, o: FuncObject):
        return self.class_interpretation_list[class_num].contains(o)
    
    @property
    def binary_interpretation_tuples(self) -> List[Tuple[FuncObject, FuncObject]]:
        return (list(self.overtaking_interpretation.get_tuples()) +
                list(self.head_on_interpretation.get_tuples()) + 
                list(self.crossing_interpretation.get_tuples()))
    
    @property
    def os_object(self) -> FuncObject:
        return self.os_interpretation.next
    
    @property
    def size(self) -> int:
        return len(self.func_objects)
        
    
    @property
    def all_object_pairs(self) -> Set[Tuple[FuncObject, FuncObject]]:
        return {(oi, oj) for oi, oj in combinations(self.func_objects, 2)}
    
    @property
    def not_in_colreg_pairs(self):
        not_in_colreg_pairs : Set[Tuple[FuncObject, FuncObject]] = set()
        for o1, o2 in self.all_object_pairs:
            if not self.in_colreg_rel(o1, o2):
                not_in_colreg_pairs.add((o1, o2))
        return not_in_colreg_pairs
    
    def shape_hash(self, hops: int = 1) -> int:
        """
        Compute the hash of the node attributes and their neighborhoods up to the given number of hops.
        
        :param hops: Number of hops to consider in the neighborhood.
        :return: Hash of the neighborhood information.
        """
        
            
        
        # Initialize a dictionary to store neighborhoods for all hop levels
        neighborhoods: Dict[int, Dict[FuncObject, tuple]] = defaultdict(dict)
        neighborhood_counter : Dict[int, Dict[FuncObject, Dict[tuple, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        def generate_tuples(hop : int, interpretation : BinaryInterpretation, node : FuncObject) -> Set[tuple]:
            relation_descs = interpretation.get_relation_descs(node)
            tuples : set[tuple] = set()
            for rd in relation_descs:
                nbh = None if hop == 0 else neighborhoods[hop - 1][rd[2]]
                t = (rd[0], rd[1], nbh)
                neighborhood_counter[hop][node][t] += 1
                tuples.add((*t, neighborhood_counter[hop][node][t]))
            return tuples
                    
        
        # Initialize base (0-hop) attributes
        for node in self.func_objects:
            attributes: Set[tuple] = set()
            if self.os_interpretation.contains(node):
                attributes.add((OSInterpretation.name, 1))
            if self.ts_interpretation.contains(node):
                attributes.add((TSInterpretation.name, 1))
            
            attributes.update(generate_tuples(0, self.overtaking_interpretation, node))
            attributes.update(generate_tuples(0, self.head_on_interpretation, node))
            attributes.update(generate_tuples(0, self.crossing_interpretation, node))
            
            neighborhoods[0][node] = (None, frozenset(attributes))

        # Build neighborhoods iteratively for each hop
        for hop in range(1, hops + 1):
            neighborhoods[hop] = {}
            for node in self.func_objects:
                attributes: Set[tuple] = set()
                if self.os_interpretation.contains(node):
                    attributes.add((OSInterpretation.name, 1))
                if self.ts_interpretation.contains(node):
                    attributes.add((TSInterpretation.name, 1))
                    
                attributes.update(generate_tuples(hop, self.overtaking_interpretation, node))
                attributes.update(generate_tuples(hop, self.head_on_interpretation, node))
                attributes.update(generate_tuples(hop, self.crossing_interpretation, node))
                
                neighborhoods[hop][node] = (neighborhoods[hop - 1][node], frozenset(attributes))

        # Return hash of the last neighborhood
        shape = frozenset(neighborhoods[hops].values())
        return hash(shape)
            