from typing import List
from model.colreg_situation import Relation
from model.vessel import VesselDesc
from model.relation_types import RelationType

class ColregSituationDesc():
    def __init__(self, vd1 : VesselDesc, colreg_class : Relation.__class__, vd2 : VesselDesc) -> None:
        self.vd1 = vd1
        self.colreg_class = colreg_class
        self.vd2 = vd2
        
class RelationDesc():
    def __init__(self, vd1 : VesselDesc, relations : List[RelationType], vd2 : VesselDesc) -> None:
        self.vd1 = vd1
        self.relations = relations
        self.vd2 = vd2