from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Dict, List, Set, Tuple, Union
from functional_level.metamodels.relation_class import RelationClass, RelationClassClause
from functional_level.metamodels.vessel_class import FuncObject, VesselClass
from logical_level.models.constraint_types import OutVisOrNoCollide
import copy
from functional_level.metamodels.interpretation import (
    HeadOnInterpretation, Interpretation, OvertakingInterpretation, CrossingFromPortInterpretation, OSInterpretation, TSInterpretation)

class FunctionalScenario2():
    def __init__(self, group : str, id, func_objects : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        self.group = group
        self.id = id
        self.func_objects = sorted(func_objects, key=lambda x: x.id)
        self.name = f'{str(len(func_objects))}vessel_{group}_{id}'
        if len(relation_desc_clauses) == 0:
            self.relation_desc_clauses = [RelationClassClause([])]
        elif isinstance(relation_desc_clauses[0], RelationClass):                   
            self.relation_desc_clauses = [RelationClassClause(relation_desc_clauses)]
        else:
            self.relation_desc_clauses = copy.deepcopy(relation_desc_clauses)

        all_pairs = [(vdi, vdj) for vdi, vdj in combinations(func_objects, 2)]
        for clause in self.relation_desc_clauses:
            existing_pairs = [(rel_desc.vd1, rel_desc.vd2) for rel_desc in clause.relation_descs]
            
            for vdi, vdj in all_pairs:
                if (vdi, vdj) not in existing_pairs and (vdj, vdi) not in existing_pairs:
                    clause.append(RelationClass(vdi, [OutVisOrNoCollide()] , vdj))
        self.relation_desc_clauses
    
    @property
    def vessel_num(self) -> int:
        return len(self.func_objects)
    
@dataclass(frozen=True)
class FunctionalScenario():
    group : str
    id : str
    os_interpretation : OSInterpretation = OSInterpretation()
    ts_interpretation : TSInterpretation = TSInterpretation()
    head_on_interpretations : HeadOnInterpretation = HeadOnInterpretation()
    overtaking_interpretations : OvertakingInterpretation = OvertakingInterpretation()
    crossing_interpretations : CrossingFromPortInterpretation = CrossingFromPortInterpretation()
    
    func_objects : List[FuncObject] = field(init=False)
    
    def __post_init__(self):
        object_set : Set[FuncObject] = set()
        for interpretations in [self.os_interpretation, self.ts_interpretation, self.head_on_interpretations, self.overtaking_interpretations, self.crossing_interpretations]:
            for interpretation in interpretations:
                for func_object in interpretation:
                    object_set.add(func_object)
        object.__setattr__(self, 'func_objects', sorted(list(object_set), key=lambda x: x.id))
        head_on_interpretation_temp = copy(self.head_on_interpretations)
        for tup in head_on_interpretation_temp:
            self.head_on_interpretations.add(tup)
        
    
    @property
    def name(self):
        return f'{str(len(self.func_objects))}vessel_{self.group}_{self.id}'
    
    def in_colreg_rel(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return self.colreg_rel(o1, o2) or self.colreg_rel(o2, o1)
    
    def in_overtaking(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return self.overtaking(o1, o2) or self.overtaking(o2, o1)
    
    def in_crossing(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return self.crossing(o1, o2) or self.crossing(o2, o1)
    
    def colreg_rel(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return self.head_on(o1, o2) or self.overtaking(o1, o2) or self.crossing(o1, o2)
    
    def head_on(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return self.head_on_interpretations.contains((o1, o2))
    
    def overtaking(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return self.overtaking_interpretations.contains((o1, o2))
    
    def crossing(self, o1 : FuncObject, o2 : FuncObject) -> bool:
        return self.crossing_interpretations.contains((o1, o2))
    
    @property
    def all_object_pairs(self) -> Set[Tuple[FuncObject, FuncObject]]:
        return {(oi, oj) for oi, oj in combinations(self.func_objects, 2)}
    
    @property
    def not_in_colreg_pairs(self):
        not_in_colreg_pairs : Set[Tuple[FuncObject, FuncObject]] = set()
        for o1, o2 in self.all_object_pairs:
            if not self.in_colreg_rel(o1, o2) and (o1, o2) not in not_in_colreg_pairs and (o2, o1) not in not_in_colreg_pairs:
                not_in_colreg_pairs.add(o1, o2)
        return not_in_colreg_pairs
    
    def shape_hash(self, hops: int = 1):
        """
        Compute the hash of the node attributes and their neighborhoods up to the given number of hops.
        
        :param hops: Number of hops to consider in the neighborhood.
        :return: Hash of the neighborhood information.
        """
        # Initialize a dictionary to store neighborhoods for all hop levels
        neighborhoods: Dict[int, Dict[FuncObject, Tuple]] = {0: {}}
        
        # Initialize base (0-hop) attributes
        for node in self.func_objects:
            attributes: Set[tuple] = set()
            if self.os_interpretation.contains(node):
                attributes.add((OSInterpretation.name, 1))
            if self.ts_interpretation.contains(node):
                attributes.add((TSInterpretation.name, 1))
            relation_descs = self.overtaking_interpretations.get_relation_descs(node)
            attributes.update((rd[0], rd[1], None) for rd in relation_descs)
            relation_descs = self.head_on_interpretations.get_relation_descs(node)
            attributes.update((rd[0], rd[1], None) for rd in relation_descs)
            relation_descs = self.crossing_interpretations.get_relation_descs(node)
            attributes.update((rd[0], rd[1], None) for rd in relation_descs)
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
                relation_descs = self.overtaking_interpretations.get_relation_descs(node)
                attributes.update((rd[0], rd[1], neighborhoods[hop - 1][rd[2]]) for rd in relation_descs)
                relation_descs = self.head_on_interpretations.get_relation_descs(node)
                attributes.update((rd[0], rd[1], neighborhoods[hop - 1][rd[2]]) for rd in relation_descs)
                relation_descs = self.crossing_interpretations.get_relation_descs(node)
                attributes.update((rd[0], rd[1], neighborhoods[hop - 1][rd[2]]) for rd in relation_descs)
                neighborhoods[hop][node] = (neighborhoods[hop - 1][node], frozenset(attributes))

        # Return hash of the last neighborhood
        return hash(frozenset(neighborhoods[hops].values()))
            
    
                    
class MSREnvironmentDesc(FunctionalScenario):
    group = 'MSR'
    def __init__(self, id, vessel_objects : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_objects, relation_desc_clauses)
        
class SBOEnvironmentDesc(FunctionalScenario):
    group = 'SBO'
    def __init__(self, id, vessel_objects : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_objects, relation_desc_clauses)
       
       
       
        
class F3EnvironmentDesc(FunctionalScenario):
    group = 'F3'
    def __init__(self, id, vessel_objects : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_objects, relation_desc_clauses)
        
        
class F2EnvironmentDesc(FunctionalScenario):
    group = 'F2'
    def __init__(self, id, vessel_objects : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_objects, relation_desc_clauses)
        
        
class F1EnvironmentDesc(FunctionalScenario):
    group = 'F1'
    def __init__(self, id,vessel_objects : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_objects, relation_desc_clauses)
                
                
