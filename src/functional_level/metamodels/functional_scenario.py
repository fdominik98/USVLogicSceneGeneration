from itertools import combinations
from typing import List, Union
from functional_level.metamodels.relation_class import RelationClass, RelationClassClause
from functional_level.metamodels.vessel_class import VesselClass
from asv_utils import VARIABLE_NUM
from logical_level.models.relation_types import OutVisOrNoCollide
import copy

class FunctionalScenario():
    def __init__(self, group : str, id, vessel_descs : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        self.group = group
        self.id = id
        self.vessel_descs = sorted(vessel_descs, key=lambda x: x.id)
        self.name = f'{str(len(vessel_descs))}vessel_{group}_{id}'
        if len(relation_desc_clauses) == 0:
            self.relation_desc_clauses = [RelationClassClause([])]
        elif isinstance(relation_desc_clauses[0], RelationClass):                   
            self.relation_desc_clauses = [RelationClassClause(relation_desc_clauses)]
        else:
            self.relation_desc_clauses = copy.deepcopy(relation_desc_clauses)

        all_pairs = [(vdi, vdj) for vdi, vdj in combinations(vessel_descs, 2)]
        for clause in self.relation_desc_clauses:
            existing_pairs = [(rel_desc.vd1, rel_desc.vd2) for rel_desc in clause.relation_descs]
            
            for vdi, vdj in all_pairs:
                if (vdi, vdj) not in existing_pairs and (vdj, vdi) not in existing_pairs:
                    clause.append(RelationClass(vdi, [OutVisOrNoCollide()] , vdj))
        self.relation_desc_clauses
    
    @property
    def vessel_num(self) -> int:
        return len(self.vessel_descs)
                    
class MSREnvironmentDesc(FunctionalScenario):
    group = 'MSR'
    def __init__(self, id, vessel_descs : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
        
class SBOEnvironmentDesc(FunctionalScenario):
    group = 'SBO'
    def __init__(self, id, vessel_descs : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
       
       
       
        
class F3EnvironmentDesc(FunctionalScenario):
    group = 'F3'
    def __init__(self, id, vessel_descs : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
        
        
class F2EnvironmentDesc(FunctionalScenario):
    group = 'F2'
    def __init__(self, id, vessel_descs : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
        
        
class F1EnvironmentDesc(FunctionalScenario):
    group = 'F1'
    def __init__(self, id,vessel_descs : List[VesselClass], relation_desc_clauses : Union[List[RelationClassClause], List[RelationClass]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
                
                
