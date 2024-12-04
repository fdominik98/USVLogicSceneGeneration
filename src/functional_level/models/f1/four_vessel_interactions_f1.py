from functional_level.metamodels.functional_scenario import F1EnvironmentDesc
from functional_level.metamodels.relation_class import RelationClass
from logical_level.models.relation_types import AtVis
from functional_level.models.model_utils import _OS, TS1, TS2, TS3

four_vessel_interactions = [
        F1EnvironmentDesc('4_vessel_1_f1',
                        [_OS, TS1, TS2, TS3],
                        [RelationClass(TS1, [AtVis()], _OS),                        
                        RelationClass(_OS, [AtVis()], TS2),
                        RelationClass(_OS, [AtVis()], TS3)])
        ]