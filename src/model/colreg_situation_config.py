from typing import Optional
from model.colreg_situation import ColregSituation

class ColregSituationConfig():
    def __init__(self, id1 : int, colreg_class : ColregSituation.__class__, id2 : int, distance : Optional[tuple[float, float]]) -> None:
        self.id1 = id1
        self.colreg_class = colreg_class
        self.id2 = id2
        self.distance = distance