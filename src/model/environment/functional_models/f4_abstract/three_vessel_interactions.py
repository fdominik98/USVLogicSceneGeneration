from model.environment.usv_environment_desc import F4AbstractEnvironmentDesc
from model.relation import RelationDescClause, RelationDesc
from model.relation_types import any_colreg_init, overtaking_or_crossing_init
from model.environment.functional_models.model_utils import OS, TS1, TS2, generate_abstract_models

blabla = four_vessel_interactions = generate_abstract_models([TS1, TS2])

three_vessel_interactions = [
        F4AbstractEnvironmentDesc('three_vessel_1_f4_abstract',
                                [OS, TS1, TS2],
                                [RelationDescClause([
                                        RelationDesc(TS1, [overtaking_or_crossing_init()], OS),
                                        RelationDesc(OS, [any_colreg_init()], TS2)]),
                                
                                RelationDescClause([
                                        RelationDesc(OS, [any_colreg_init()], TS1),
                                        RelationDesc(TS2, [overtaking_or_crossing_init()], OS)]),
                                
                                ]),
        ]   