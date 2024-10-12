from itertools import combinations
from typing import List, Union
from model.relation import RelationDesc, RelationDescClause
from model.vessel import VesselDesc
from model.environment.usv_config import VARIABLE_NUM
from model.relation_types import OutVisOrNoCollide
import copy

class USVEnvironmentDesc():
    def __init__(self, group : str, id, vessel_descs : List[VesselDesc], relation_desc_clauses : Union[List[RelationDescClause], List[RelationDesc]]) -> None:
        self.group = group
        self.id = id
        self.vessel_descs = sorted(vessel_descs, key=lambda x: x.id)
        self.name = f'{str(len(vessel_descs))}vessel_{group}_{id}'
        if len(relation_desc_clauses) == 0:
            self.relation_desc_clauses = [RelationDescClause([])]
        elif isinstance(relation_desc_clauses[0], RelationDesc):                   
            self.relation_desc_clauses = [RelationDescClause(relation_desc_clauses)]
        else:
            self.relation_desc_clauses = copy.deepcopy(relation_desc_clauses)
            
        self.vessel_num = len(vessel_descs)
        self.all_variable_num = VARIABLE_NUM * self.vessel_num - (VARIABLE_NUM - 1)

        all_pairs = [(vdi, vdj) for vdi, vdj in combinations(vessel_descs, 2)]
        for clause in self.relation_desc_clauses:
            existing_pairs = [(rel_desc.vd1, rel_desc.vd2) for rel_desc in clause.relation_descs]
            
            for vdi, vdj in all_pairs:
                if (vdi, vdj) not in existing_pairs and (vdj, vdi) not in existing_pairs:
                    clause.append(RelationDesc(vdi, [OutVisOrNoCollide()] , vdj))
        self.relation_desc_clauses
    
class F4AbstractEnvironmentDesc(USVEnvironmentDesc):
    group = 'F4_Abstract'
    def __init__(self, id, vessel_descs : List[VesselDesc], relation_desc_clauses : Union[List[RelationDescClause], List[RelationDesc]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
                    
class F4EnvironmentDesc(USVEnvironmentDesc):
    group = 'F4'
    def __init__(self, id, vessel_descs : List[VesselDesc], relation_desc_clauses : Union[List[RelationDescClause], List[RelationDesc]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
        
class F3EnvironmentDesc(USVEnvironmentDesc):
    group = 'F3'
    def __init__(self, id, vessel_descs : List[VesselDesc], relation_desc_clauses : Union[List[RelationDescClause], List[RelationDesc]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
        
        
class F2EnvironmentDesc(USVEnvironmentDesc):
    group = 'F2'
    def __init__(self, id, vessel_descs : List[VesselDesc], relation_desc_clauses : Union[List[RelationDescClause], List[RelationDesc]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
        
        
class F1EnvironmentDesc(USVEnvironmentDesc):
    group = 'F1'
    def __init__(self, id,vessel_descs : List[VesselDesc], relation_desc_clauses : Union[List[RelationDescClause], List[RelationDesc]]) -> None:
        super().__init__(self.group, id, vessel_descs, relation_desc_clauses)
                
                
