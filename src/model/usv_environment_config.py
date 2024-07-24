from itertools import combinations
from model.colreg_situation_config import ColregSituationConfig
from model.colreg_situation import NoColreg
from model.usv_config import range_far

class USVEnvironmentConfig():
    def __init__(self, name, radii : list[float], colreg_situations : list[ColregSituationConfig]) -> None:
        self.name = name
        self.radii = radii
        self.colreg_situations = colreg_situations
        self.actor_num = len(radii)
        self.variable_num = self.actor_num * 4
        self.col_sit_num = len(self.colreg_situations)   
        

        all_pairs = [(i, j) for i, j in combinations(range(self.actor_num), 2)]
        existing_pairs = [(colreg_config.id1, colreg_config.id2) for colreg_config in colreg_situations]
        
        for i, j in all_pairs:
            if (i, j) not in existing_pairs and (j, i) not in existing_pairs:
                colreg_situations.append(ColregSituationConfig(i, NoColreg, j, range_far(self.actor_num)))
                
