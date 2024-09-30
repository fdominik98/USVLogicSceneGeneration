from itertools import combinations
from typing import List
from model.relation import RelationDesc
from model.vessel import VesselDesc
from model.environment.usv_config import VARIABLE_NUM
from model.relation_types import OutVisOrNoCollide

class USVEnvironmentDesc():
    def __init__(self, name, vessel_descs : List[VesselDesc], relation_descs : List[RelationDesc]) -> None:
        self.name = name
        self.vessel_descs = sorted(vessel_descs, key=lambda v: v.id)
        self.relation_descs = relation_descs
        self.actor_num = len(vessel_descs)
        self.all_variable_num = VARIABLE_NUM * self.actor_num - 3
        self.col_sit_num = len(self.relation_descs)   
        

        all_pairs = [(i, j) for i, j in combinations(range(self.actor_num), 2)]
        existing_pairs = [(rel_desc.vd1, rel_desc.vd2) for rel_desc in relation_descs]
        
        for i, j in all_pairs:
            vd1 = vessel_descs[i]
            vd2 = vessel_descs[j]
            if (vd2, vd1) not in existing_pairs and (vd1, vd2) not in existing_pairs:
                relation_descs.append(RelationDesc(vd1, [OutVisOrNoCollide()] , vd2))
                
                
