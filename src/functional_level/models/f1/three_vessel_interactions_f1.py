from functional_level.metamodels.functional_scenario import F1EnvironmentDesc
from functional_level.metamodels.relation_class import RelationClass
from logical_level.models.constraint_types import AtVis
from functional_level.models.model_utils import _OS, TS1, TS2

three_vessel_interactions = [
        F1EnvironmentDesc('3_vessel_1_f1',
                        [_OS, TS1, TS2],
                        [RelationClass(_OS, [AtVis()], TS1),
                        RelationClass(TS2, [AtVis()], _OS),
                        RelationClass(TS1, [AtVis()], TS2)])
        ]