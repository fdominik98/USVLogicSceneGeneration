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
        self.name = f'{str(len(vessel_descs))}vessel_{group}_{id}'
        self.vessel_descs = sorted(vessel_descs, key=lambda v: v.id) 
        if len(relation_desc_clauses) == 0:
            self.relation_dec_clauses = [RelationDescClause()]
        elif isinstance(relation_desc_clauses[0], RelationDesc):                   
            self.relation_dec_clauses = [RelationDescClause(relation_desc_clauses)]
        else:
            self.relation_dec_clauses = copy.deepcopy(relation_desc_clauses)
            
        self.vessel_num = len(vessel_descs)
        self.all_variable_num = VARIABLE_NUM * self.vessel_num - 3

        for clause in self.relation_dec_clauses:
            all_pairs = [(i, j) for i, j in combinations(range(self.vessel_num), 2)]
            existing_pairs = [(rel_desc.vd1, rel_desc.vd2) for rel_desc in clause.relation_descs]
            
            for i, j in all_pairs:
                vd1 = vessel_descs[i]
                vd2 = vessel_descs[j]
                if (vd2, vd1) not in existing_pairs and (vd1, vd2) not in existing_pairs:
                    clause.append(RelationDesc(vd1, [OutVisOrNoCollide()] , vd2))
        self.relation_dec_clauses
    
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
                
                
