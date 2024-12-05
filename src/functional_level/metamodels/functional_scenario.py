from dataclasses import dataclass, field
from itertools import combinations
from typing import List, Union
from functional_level.metamodels.relation_class import RelationClass, RelationClassClause
from functional_level.metamodels.vessel_class import FuncObject, VesselClass
from logical_level.models.relation_types import OutVisOrNoCollide
import copy
from functional_level.metamodels.interpretation import (
    HeadOnInterpretation, OvertakingInterpretation, CrossingFromPortInterpretation, OSInterpretation, TSInterpretation)

class FunctionalScenario():
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
class FunctionalScenario2():
    group : str
    id : str
    os_interpretation : OSInterpretation = OSInterpretation()
    ts_interpretation : TSInterpretation = TSInterpretation()
    head_on_interpretations : HeadOnInterpretation = HeadOnInterpretation()
    overtaking_interpretations : OvertakingInterpretation = OvertakingInterpretation()
    crossing_interpretations : CrossingFromPortInterpretation = CrossingFromPortInterpretation()
    
    func_objects : List[FuncObject] = field(init=False)
    
    self.vessel_objects = sorted(vessel_objects, key=lambda x: x.id)
    
    @property
    def name(self):
        return f'{str(len(self.func_objects))}vessel_{self.group}_{id}'
                    
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
                
                
