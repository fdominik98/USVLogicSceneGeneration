from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Optional, Set, Tuple
import copy
from functional_level.metamodels.functional_object import FuncObject
from functional_level.metamodels.interpretation import (
    BinaryInterpretation, StaticObstacleInterpretation, headOnInterpretation, overtakingInterpretation,
    crossingFromPortInterpretation, OSInterpretation, TSInterpretation, VesselInterpretation, VesselTypeInterpretation,
    StaticObstacleTypeInterpretation, inHeadOnSectorInterpretation, inPortSideSectorInterpretation,
    inStarboardSideSectorInterpretation, inSternSectorInterpretation, staticObstacleTypeInterpretation, vesselTypeInterpretation)
from utils.scenario import Scenario
   
@dataclass(frozen=True)
class FunctionalScenario(Scenario):
    OS_interpretation : OSInterpretation = OSInterpretation()
    TS_interpretation : TSInterpretation = TSInterpretation()
    Static_obstacle_interpretation : StaticObstacleInterpretation = StaticObstacleInterpretation()
    
    Vessel_type_interpretation : VesselTypeInterpretation = VesselTypeInterpretation()
    Static_obstacle_type_interpretation : StaticObstacleTypeInterpretation = StaticObstacleTypeInterpretation()
    
    head_on_interpretation : headOnInterpretation = headOnInterpretation()
    overtaking_interpretation : overtakingInterpretation = overtakingInterpretation()
    crossing_from_port_interpretation : crossingFromPortInterpretation = crossingFromPortInterpretation()
    
    in_head_on_sector_interpretation : inHeadOnSectorInterpretation = inHeadOnSectorInterpretation()
    in_port_side_sector_interpretation : inPortSideSectorInterpretation = inPortSideSectorInterpretation()
    in_starboard_side_sector_interpretation : inStarboardSideSectorInterpretation = inStarboardSideSectorInterpretation()
    in_stern_sector_interpretation : inSternSectorInterpretation = inSternSectorInterpretation()
    
    vessel_type_interpretation : vesselTypeInterpretation = vesselTypeInterpretation()
    static_obstacle_type_interpretation : staticObstacleTypeInterpretation = staticObstacleTypeInterpretation()
    
    func_objects : List[FuncObject] = field(init=False)
    Vessel_interpretation : VesselInterpretation = field(init=False)
    
    def __post_init__(self):
        object_set : Set[FuncObject] = set()
        for interpretations in [self.OS_interpretation, self.TS_interpretation, self.head_on_interpretation, self.overtaking_interpretation, self.crossing_from_port_interpretation]:
            for interpretation in interpretations:
                for func_object in interpretation:
                    object_set.add(func_object)
        object.__setattr__(self, 'func_objects', sorted(list(object_set), key=lambda x: x.id))
        
        object.__setattr__(self, 'Vessel_interpretation', VesselInterpretation(self.OS_interpretation._data.union(self.TS_interpretation._data)))
        
        head_on_interpretation_temp = copy.deepcopy(self.head_on_interpretation)
        for o1, o2 in head_on_interpretation_temp:
            self.head_on_interpretation.add(o1, o2)
        
    
    def in_colreg_rel(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.colreg_rel(o1, o2) or self.colreg_rel(o2, o1)
    
    def in_overtaking(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.overtaking(o1, o2) or self.overtaking(o2, o1)
    
    def in_crossing_from_port(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.crossing_from_port(o1, o2) or self.crossing_from_port(o2, o1)
    
    def colreg_rel(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.head_on(o1, o2) or self.overtaking(o1, o2) or self.crossing_from_port(o1, o2)
    
    def head_on(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.head_on_interpretation.contains((o1, o2))
    
    def overtaking(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.overtaking_interpretation.contains((o1, o2))
    
    def crossing_from_port(self, o1 : Optional[FuncObject], o2 : Optional[FuncObject]) -> bool:
        return self.crossing_from_port_interpretation.contains((o1, o2))
    
    def is_os(self, o : FuncObject) -> bool:
        return self.OS_interpretation.contains(o)
    
    def is_ts(self, o : FuncObject) -> bool:
        return self.TS_interpretation.contains(o)
    
    def is_vessel(self, o : FuncObject) -> bool:
        return self.Vessel_interpretation.contains(o)
    
    def is_obstacle(self, o : FuncObject) -> bool:
        return self.Static_obstacle_interpretation.contains(o)
    
    def is_vessel_class_x(self, class_num : int, o: FuncObject):
        raise NotImplementedError()
    
    @property
    def binary_interpretation_tuples(self) -> List[Tuple[FuncObject, FuncObject]]:
        return (list(self.overtaking_interpretation.get_tuples()) +
                list(self.head_on_interpretation.get_tuples()) + 
                list(self.crossing_from_port_interpretation.get_tuples()))
    
    
    @property
    def ts_objects(self) -> Set[FuncObject]:
        return {ts for ts, in self.TS_interpretation._data}
    
    @property
    def os_object(self) -> FuncObject:
        return self.OS_interpretation.next
    
    @property
    def obstacle_number(self) -> int:
        return len(self.Static_obstacle_interpretation)
    
    @property
    def vessel_number(self) -> int:
        return len(self.Vessel_interpretation)        
    
    @property
    def all_object_pairs(self) -> Set[Tuple[FuncObject, FuncObject]]:
        return {(oi, oj) for oi, oj in combinations(self.func_objects, 2)}
    
    @property
    def os_ts_pairs(self) -> Set[Tuple[FuncObject, FuncObject]]:
        os = self.os_object
        return {(os, obj) for obj in self.ts_objects}
    
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
            if self.OS_interpretation.contains(node):
                attributes.add((OSInterpretation.name, 1))
            if self.TS_interpretation.contains(node):
                attributes.add((TSInterpretation.name, 1))
            
            attributes.update(generate_tuples(0, self.overtaking_interpretation, node))
            attributes.update(generate_tuples(0, self.head_on_interpretation, node))
            attributes.update(generate_tuples(0, self.crossing_from_port_interpretation, node))
            
            neighborhoods[0][node] = (None, frozenset(attributes))

        # Build neighborhoods iteratively for each hop
        for hop in range(1, hops + 1):
            neighborhoods[hop] = {}
            for node in self.func_objects:
                attributes: Set[tuple] = set()
                if self.OS_interpretation.contains(node):
                    attributes.add((OSInterpretation.name, 1))
                if self.TS_interpretation.contains(node):
                    attributes.add((TSInterpretation.name, 1))
                    
                attributes.update(generate_tuples(hop, self.overtaking_interpretation, node))
                attributes.update(generate_tuples(hop, self.head_on_interpretation, node))
                attributes.update(generate_tuples(hop, self.crossing_from_port_interpretation, node))
                
                neighborhoods[hop][node] = (neighborhoods[hop - 1][node], frozenset(attributes))

        # Return hash of the last neighborhood
        shape = frozenset(neighborhoods[hops].values())
        return hash(shape)
            