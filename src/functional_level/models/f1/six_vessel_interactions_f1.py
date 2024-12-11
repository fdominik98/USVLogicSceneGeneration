from functional_level.metamodels.functional_scenario import F1EnvironmentDesc
from logical_level.models.constraint_types import AtVis
from functional_level.metamodels.relation_class import RelationClass
from functional_level.models.model_utils import _OS, TS1, TS2, TS3, TS4, TS5

six_vessel_interactions = [
        F1EnvironmentDesc('6_vessel_1_f1',
                [_OS, TS1, TS2, TS3, TS4, TS5],
                [RelationClass(TS1, [AtVis()], _OS),
                RelationClass(_OS, [AtVis()], TS2),
                RelationClass(TS3, [AtVis()], _OS),
                RelationClass(_OS, [AtVis()], TS4),
                RelationClass(_OS, [AtVis()], TS5)])
        ]
    