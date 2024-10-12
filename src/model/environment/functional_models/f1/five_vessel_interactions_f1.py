from model.relation import RelationDesc
from model.relation_types import AtVis
from model.environment.usv_environment_desc import F1EnvironmentDesc
from model.environment.functional_models.model_utils import _OS, TS1, TS2, TS3, TS4

five_vessel_interactions = [
        F1EnvironmentDesc('5_vessel_1_f1',
                [_OS, TS1, TS2, TS3, TS4],
                [RelationDesc(TS1, [AtVis()], _OS),
                RelationDesc(TS2, [AtVis()], _OS),
                RelationDesc(_OS, [AtVis()], TS3),
                RelationDesc(TS4, [AtVis()], _OS)])]   