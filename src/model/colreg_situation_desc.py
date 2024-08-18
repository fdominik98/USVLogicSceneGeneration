from typing import Optional
from model.colreg_situation import ColregSituation
from model.vessel import VesselDesc

class ColregSituationDesc():
    def __init__(self, vd1 : VesselDesc, colreg_class : ColregSituation.__class__, vd2 : VesselDesc, distance : Optional[tuple[float, float]]) -> None:
        self.vd1 = vd1
        self.colreg_class = colreg_class
        self.vd2 = vd2
        self.distance = distance