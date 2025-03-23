from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations, permutations
from typing import Dict, List, Optional, Set, Tuple
from functional_level.metamodels.functional_object import FuncObject
from functional_level.metamodels.interpretation import (
    BinaryInterpretation, SeaObjectInterpretation, StaticObstacleInterpretation, atVisibilityDistanceInterpretation, headOnInterpretation,
    inVisibilityDistanceInterpretation, mayCollideInterpretation, outVisibilityDistanceInterpretation,  OSInterpretation, TSInterpretation,
    VesselInterpretation, VesselTypeInterpretation, StaticObstacleTypeInterpretation, inHeadOnSectorOfInterpretation, 
    inPortSideSectorOfInterpretation, inStarboardSideSectorOfInterpretation, inSternSectorOfInterpretation, 
    staticObstacleTypeInterpretation, vesselTypeInterpretation, overtakingToPortInterpretation, overtakingToStarboardInterpretation,
    crossingFromPortInterpretation, dangerousHeadOnSectorOfInterpretation)
from utils.scenario import Scenario
   
@dataclass(frozen=True)
class FunctionalScenario(Scenario):
    Sea_object_interpretation : SeaObjectInterpretation = field(init=False)
    Vessel_interpretation : VesselInterpretation = field(init=False)
    OS_interpretation : OSInterpretation = OSInterpretation()
    TS_interpretation : TSInterpretation = TSInterpretation()
    Static_obstacle_interpretation : StaticObstacleInterpretation = StaticObstacleInterpretation()
    Vessel_type_interpretation : VesselTypeInterpretation = VesselTypeInterpretation()
    Static_obstacle_type_interpretation : StaticObstacleTypeInterpretation = StaticObstacleTypeInterpretation()
    
    
    out_visibility_distance_interpretation : outVisibilityDistanceInterpretation = outVisibilityDistanceInterpretation()
    at_visibility_distance_interpretation : atVisibilityDistanceInterpretation = atVisibilityDistanceInterpretation()
    in_visibility_distance_interpretation : inVisibilityDistanceInterpretation = inVisibilityDistanceInterpretation()
    
    may_collide_interpretation : mayCollideInterpretation = mayCollideInterpretation()
    
    in_head_on_sector_of_interpretation : inHeadOnSectorOfInterpretation = inHeadOnSectorOfInterpretation()
    in_port_side_sector_of_interpretation : inPortSideSectorOfInterpretation = inPortSideSectorOfInterpretation()
    in_starboard_side_sector_of_interpretation : inStarboardSideSectorOfInterpretation = inStarboardSideSectorOfInterpretation()
    in_stern_sector_of_interpretation : inSternSectorOfInterpretation = inSternSectorOfInterpretation()
    
    vessel_type_interpretation : vesselTypeInterpretation = vesselTypeInterpretation()
    static_obstacle_type_interpretation : staticObstacleTypeInterpretation = staticObstacleTypeInterpretation()
    
    sorted_sea_objects : List[FuncObject] = field(init=False)
    

    head_on_interpretation : headOnInterpretation = field(default=headOnInterpretation(), init=False)
    overtaking_to_port_interpretation : overtakingToPortInterpretation = field(default=overtakingToPortInterpretation(), init=False)
    overtaking_to_starboard_interpretation : overtakingToStarboardInterpretation = field(default=overtakingToStarboardInterpretation(), init=False)
    crossing_from_port_interpretation : crossingFromPortInterpretation = field(default=crossingFromPortInterpretation(), init=False)
    dangerous_head_on_sector_of_interpretation : dangerousHeadOnSectorOfInterpretation = field(default=dangerousHeadOnSectorOfInterpretation(), init=False)
    
    
    def __post_init__(self):
        self.out_visibility_distance_interpretation.make_two_directional()
        self.in_visibility_distance_interpretation.make_two_directional()
        self.at_visibility_distance_interpretation.make_two_directional()
        self.may_collide_interpretation.make_two_directional()
        
        
        object.__setattr__(self, 'Vessel_interpretation', VesselInterpretation.union(self.OS_interpretation, self.TS_interpretation))
        object.__setattr__(self, 'Sea_object_interpretation', SeaObjectInterpretation.union(self.Vessel_interpretation, self.Static_obstacle_interpretation))
        object.__setattr__(self, 'sorted_sea_objects', sorted(list(self.sea_objects), key=lambda x: x.id))
        
        
        for o1, o2 in self.all_sea_object_pair_permutations:
            if self.head_on(o1, o2):
                self.head_on_interpretation.add(o1, o2)
                self.head_on_interpretation.add(o2, o1)
            if self.overtaking_to_port(o1, o2):
                self.overtaking_to_port_interpretation.add(o1, o2)
            if self.overtaking_to_port(o2, o1):
                self.overtaking_to_port_interpretation.add(o2, o1)
            if self.overtaking_to_starboard(o1, o2):
                self.overtaking_to_starboard_interpretation.add(o1, o2)
            if self.overtaking_to_starboard(o2, o1):
                self.overtaking_to_starboard_interpretation.add(o2, o1)
            if self.crossing_from_port(o1, o2):
                self.crossing_from_port_interpretation.add(o1, o2)
            if self.crossing_from_port(o2, o1):
                self.crossing_from_port_interpretation.add(o2, o1)
            if self.dangerous_head_on_sector_of(o1, o2):
                self.dangerous_head_on_sector_of_interpretation.add(o1, o2)
        
        
        
    def is_os(self, o : FuncObject) -> bool:
        return self.OS_interpretation.contains(o)
    
    def is_ts(self, o : FuncObject) -> bool:
        return self.TS_interpretation.contains(o)
    
    def is_vessel(self, o : FuncObject) -> bool:
        return self.Vessel_interpretation.contains(o)
    
    def is_sea_object(self, o : FuncObject) -> bool:
        return self.Sea_object_interpretation.contains(o)
    
    def is_obstacle(self, o : FuncObject) -> bool:
        return self.Static_obstacle_interpretation.contains(o)
    
    def is_vessel_type(self, o : FuncObject) -> bool:
        return self.Vessel_type_interpretation.contains(o)
    
    def is_obstacle_type(self, o : FuncObject) -> bool:
        return self.Static_obstacle_type_interpretation.contains(o)
    
    
    
    def in_masthead_sector_of(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return (self.is_sea_object(o1) and self.is_vessel(o2) and
                    (self.in_port_side_sector_of_interpretation.contains((o1, o2)) or
                     self.in_starboard_side_sector_of_interpretation.contains((o1, o2)))
                )
        
    def at_visibility_distance_and_may_collide(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        
        return (self.is_sea_object(o1) and self.is_vessel(o2) and
                self.at_visibility_distance_interpretation.contains((o1, o2)) and
                self.may_collide_interpretation.contains((o1, o2)))
    
    def out_vis_or_may_not_collide(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return (self.is_sea_object(o1) and self.is_vessel(o2) and
                    (self.out_visibility_distance_interpretation.contains((o1, o2)) or
                    not self.may_collide_interpretation.contains((o1, o2)))
               )
    
    
    def head_on(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return (self.is_vessel(o1) and self.is_vessel(o2) and
                self.in_head_on_sector_of_interpretation.contains((o1, o2)) and
                self.in_head_on_sector_of_interpretation.contains((o2, o1)) and
                self.at_visibility_distance_and_may_collide(o1, o2))
    
    def overtaking_to_port(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return (self.is_vessel(o1) and self.is_vessel(o2) and
                self.in_stern_sector_of_interpretation.contains((o1, o2)) and
                self.in_port_side_sector_of_interpretation.contains((o2, o1)) and
                self.at_visibility_distance_and_may_collide(o1, o2))
        
    def overtaking_to_starboard(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return (self.is_vessel(o1) and self.is_vessel(o2) and
                self.in_stern_sector_of_interpretation.contains((o1, o2)) and
                self.in_starboard_side_sector_of_interpretation.contains((o2, o1)) and
                self.at_visibility_distance_and_may_collide(o1, o2))
    
    def overtaking(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return self.overtaking_to_port(o1, o2) or self.overtaking_to_starboard(o1, o2) 
        
    def crossing_from_port(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return (self.is_vessel(o1) and self.is_vessel(o2) and
                self.in_port_side_sector_of_interpretation.contains((o1, o2)) and
                self.in_starboard_side_sector_of_interpretation.contains((o2, o1)) and
                self.at_visibility_distance_and_may_collide(o1, o2) and not self.head_on(o1, o2))
        
    def give_way(self, o : FuncObject) -> bool:
        if not self.is_vessel(o):
            return False
        for o2 in self.sea_objects:
            if self.overtaking(o, o2) or self.crossing_from_port(o, o2) or self.head_on(o, o2) or self.dangerous_head_on_sector_of(o2, o):
                return True
        return False
        
    def stand_on(self, o : FuncObject) -> bool:
        if not self.is_vessel(o):
            return False
        for o2 in self.sea_objects:
            if self.overtaking(o2, o) or self.crossing_from_port(o2, o):
                return True
        return False
        
    def ambiguous(self, o : FuncObject) -> bool:
        return self.is_vessel(o) and self.give_way(o) and self.stand_on(o)
        
    def dangerous_head_on_sector_of(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return (self.is_obstacle(o1) and self.is_vessel(o2) and
                self.in_head_on_sector_of_interpretation.contains((o1, o2)) and
                self.at_visibility_distance_and_may_collide(o1, o2))
    
    def in_colregs_situation_with(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return (self.is_vessel(o1) and self.is_vessel(o2) and
                (self.head_on(o1, o2) or
                self.crossing_from_port(o1, o2) or
                self.crossing_from_port(o2, o1) or
                self.overtaking(o1, o2) or
                self.overtaking(o2, o1)))
    
    def find_vessel_type_name(self, obj : FuncObject) -> Optional[str]:
        return next((self.Vessel_interpretation.get_value(o2)
                     for o1, o2 in self.vessel_type_interpretation if o1 == obj), None)
        
    def find_obstacle_type_name(self, obj : FuncObject) -> Optional[str]:
        return next((self.Static_obstacle_interpretation.get_value(o2)
                     for o1, o2 in self.static_obstacle_type_interpretation if o1 == obj), None)
        
    @property
    def is_relevant(self) -> bool:
        os = self.os_object
        # os_obst = all(self.dangerous_head_on_sector_of(o, os) for o in self.obstacle_objects)
        # os_ts = all(self.in_colregs_situation_with(os, ts) for ts in self.ts_objects)
        # ts_ts = all(self.out_vis_or_may_not_collide(o1, o2) or self.out_vis_or_may_not_collide(o2, o1) for (o1, o2) in self.all_ts_obstacle_pair_combinations)
        
        return (all(self.in_colregs_situation_with(os, ts) for ts in self.ts_objects) and
                all(self.dangerous_head_on_sector_of(o, os) for o in self.obstacle_objects) and
                all((self.out_vis_or_may_not_collide(o1, o2) or self.out_vis_or_may_not_collide(o2, o1)) for (o1, o2) in self.all_ts_obstacle_pair_combinations))
       
    @property 
    def is_ambiguous(self) -> bool:
        return self.ambiguous(self.os_object)
        
                    
    @property
    def ts_objects(self) -> Set[FuncObject]:
        return {ts for (ts,) in self.TS_interpretation}
    
    @property
    def obstacle_objects(self) -> Set[FuncObject]:
        return {o for (o,) in self.Static_obstacle_interpretation}
    
    @property
    def vessel_types(self) -> Set[FuncObject]:
        return {o for (o,) in self.Vessel_type_interpretation}
    
    @property
    def obstacle_types(self) -> Set[FuncObject]:
        return {o for (o,) in self.Static_obstacle_type_interpretation}
    
    @property
    def functional_objects(self) -> Set[FuncObject]:
        return self.sea_objects | self.vessel_types | self.obstacle_types
    
    @property
    def os_object(self) -> FuncObject:
        return self.OS_interpretation.first
    
    @property
    def sea_objects(self) -> Set[FuncObject]:
        return {o for (o,) in self.Sea_object_interpretation}
    
    @property
    def obstacle_number(self) -> int:
        return len(self.Static_obstacle_interpretation)
    
    @property
    def vessel_number(self) -> int:
        return len(self.Vessel_interpretation)        
    
    @property
    def all_sea_object_pair_permutations(self) -> Set[Tuple[FuncObject, FuncObject]]:
        return set(permutations(self.sea_objects, 2))
    
    @property
    def all_ts_obstacle_pair_combinations(self) -> Set[Tuple[FuncObject, FuncObject]]:
        return set(combinations(self.ts_objects.union(self.obstacle_objects), 2))
    
    
    def shape_hash_hard(self, hops: int = 1) -> int:
        return self._shape_hash(hops,
            [self.in_visibility_distance_interpretation, self.at_visibility_distance_interpretation,
             self.out_visibility_distance_interpretation, self.may_collide_interpretation,
             self.in_head_on_sector_of_interpretation, self.in_port_side_sector_of_interpretation,
             self.in_starboard_side_sector_of_interpretation, self.in_stern_sector_of_interpretation,
             self.static_obstacle_type_interpretation, self.vessel_type_interpretation])
        
    def shape_hash_soft(self, hops: int = 1) -> int:
        return self._shape_hash(hops,
            [self.head_on_interpretation, self.overtaking_to_port_interpretation,
             self.overtaking_to_starboard_interpretation, self.crossing_from_port_interpretation,
             self.dangerous_head_on_sector_of_interpretation])
    
    def _shape_hash(self, hops: int, edges : List[BinaryInterpretation]) -> int:
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
        
        def create_attributes(hop: int, node: FuncObject) -> frozenset[tuple]:
            attributes: Set[tuple] = set()
            if self.Sea_object_interpretation.contains(node):
                attributes.add((self.Sea_object_interpretation.name_with_value(node), 1))
            if self.Vessel_interpretation.contains(node):
                attributes.add((self.Vessel_interpretation.name_with_value(node), 1))
            if self.OS_interpretation.contains(node):
                attributes.add((self.OS_interpretation.name_with_value(node), 1))
            if self.TS_interpretation.contains(node):
                attributes.add((self.TS_interpretation.name_with_value(node), 1))
            if self.Static_obstacle_interpretation.contains(node):
                attributes.add((self.Static_obstacle_interpretation.name_with_value(node), 1))
            if self.Vessel_type_interpretation.contains(node):
                attributes.add((self.Vessel_type_interpretation.name_with_value(node), 1))
            if self.Static_obstacle_type_interpretation.contains(node):
                attributes.add((self.Static_obstacle_type_interpretation.name_with_value(node), 1))
                
            for edge_interpretation in edges:
                attributes.update(generate_tuples(hop, edge_interpretation, node))
            
            return frozenset(attributes)
                    
        
        # Initialize base (0-hop) attributes
        for node in self.functional_objects:
            neighborhoods[0][node] = (None, create_attributes(0, node))

        # Build neighborhoods iteratively for each hop
        for hop in range(1, hops + 1):
            neighborhoods[hop] = {}
            for node in self.functional_objects:
                neighborhoods[hop][node] = (neighborhoods[hop - 1][node], create_attributes(hop, node))

        # Return hash of the last neighborhood
        shape = frozenset(neighborhoods[hops].values())
        return hash(shape)
            