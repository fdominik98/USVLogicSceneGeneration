from itertools import combinations
from typing import List
from model.colreg_situation_desc import ColregSituationDesc
from model.colreg_situation import NoColreg
from model.vessel import VesselDesc
from model.environment.usv_config import VARIABLE_NUM

class USVEnvironmentDesc():
    def __init__(self, name, vessel_descs : List[VesselDesc], colreg_situation_descs : List[ColregSituationDesc]) -> None:
        self.name = name
        self.vessel_descs = sorted(vessel_descs, key=lambda v: v.id)
        self.colreg_situation_descs = colreg_situation_descs
        self.actor_num = len(vessel_descs)
        self.all_variable_num = VARIABLE_NUM * self.actor_num - 3
        self.col_sit_num = len(self.colreg_situation_descs)   
        

        all_pairs = [(i, j) for i, j in combinations(range(self.actor_num), 2)]
        existing_pairs = [(colreg_desc.vd1, colreg_desc.vd2) for colreg_desc in colreg_situation_descs]
        
        for i, j in all_pairs:
            vd1 = vessel_descs[i]
            vd2 = vessel_descs[j]
            if (vd2, vd1) not in existing_pairs and (vd1, vd2) not in existing_pairs:
                colreg_situation_descs.append(ColregSituationDesc(vd1, NoColreg, vd2))
                
                