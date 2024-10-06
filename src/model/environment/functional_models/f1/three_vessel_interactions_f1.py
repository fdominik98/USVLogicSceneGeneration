from model.environment.usv_environment_desc import F1EnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import AtVis
from model.environment.functional_models.model_utils import OS, TS1, TS2

three_vessel_interactions = [
        F1EnvironmentDesc('3_vessel_1_f1',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [AtVis()], TS1),
                        RelationDesc(TS2, [AtVis()], OS),
                        RelationDesc(TS1, [AtVis()], TS2)])
        ]