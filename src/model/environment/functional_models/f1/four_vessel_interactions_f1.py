from model.environment.usv_environment_desc import F1EnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import AtVis
from model.environment.functional_models.model_utils import OS, TS1, TS2, TS3

four_vessel_interactions = [
        F1EnvironmentDesc('4_vessel_1_f1',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [AtVis()], OS),                        
                        RelationDesc(OS, [AtVis()], TS2),
                        RelationDesc(OS, [AtVis()], TS3)])
        ]