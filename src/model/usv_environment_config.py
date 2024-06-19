import pickle
from model.colreg_situation_config import ColregSituationConfig

class USVEnvironmentConfig():
    def __init__(self, name, radii : list[float], colreg_situations : list[ColregSituationConfig]) -> None:
        self.name = name
        self.radii = radii
        self.colreg_situations = colreg_situations
        self.actor_num = len(radii)
        self.variable_num = self.actor_num * 4
        self.col_sit_num = len(self.colreg_situations)        
