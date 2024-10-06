from model.environment.usv_environment_desc import F4AbstractEnvironmentDesc
from model.relation import RelationDescClause, RelationDesc
from model.relation_types import any_colreg_init, overtaking_or_crossing_init
from model.environment.functional_models.model_utils import OS, TS1, TS2

three_vessel_interactions = [
        F4AbstractEnvironmentDesc('three_vessel_1_f4_abstract',
                                [OS, TS1, TS2],
                                [RelationDescClause([
                                        RelationDesc(OS, [overtaking_or_crossing_init()], TS1),
                                        RelationDesc(TS2, [any_colreg_init()], OS)]),
                                
                                RelationDescClause([
                                        RelationDesc(TS1, [any_colreg_init()], OS),
                                        RelationDesc(OS, [overtaking_or_crossing_init()], TS2)]),
                                
                                ]),
        ]   