from model.environment.usv_environment_desc import F1EnvironmentDesc
from model.relation_types import AtVis
from model.relation import RelationDesc
from model.environment.functional_models.model_utils import OS, TS1, TS2, TS3, TS4, TS5

six_vessel_interactions = [
        F1EnvironmentDesc('6_vessel_1_f1',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [AtVis()], OS),
                RelationDesc(OS, [AtVis()], TS2),
                RelationDesc(TS3, [AtVis()], OS),
                RelationDesc(OS, [AtVis()], TS4),
                RelationDesc(OS, [AtVis()], TS5)])
        ]
    