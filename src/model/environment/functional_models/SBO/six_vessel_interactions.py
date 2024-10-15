from model.environment.functional_models.model_utils import _OS, TS1, TS2, TS3, TS4, TS5
from model.environment.usv_environment_desc import SBOEnvironmentDesc
from model.relation import RelationDesc, RelationDescClause
from model.relation_types import any_colreg_init, overtaking_or_crossing_init

six_vessel_interactions = [
        SBOEnvironmentDesc(1, [_OS, TS1, TS2, TS3, TS4, TS5],
                        [RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS3),
                            RelationDesc(_OS, any_colreg_init(), TS4),
                            RelationDesc(_OS, any_colreg_init(), TS5)]),                         
                        RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(TS3, any_colreg_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS4),
                            RelationDesc(_OS, any_colreg_init(), TS5)]),
                        RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS3),
                            RelationDesc(TS4, any_colreg_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS5)]),
                        RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(TS3, any_colreg_init(), _OS),
                            RelationDesc(TS4, any_colreg_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS5)]),                        
                        RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS3),
                            RelationDesc(_OS, any_colreg_init(), TS4),
                            RelationDesc(TS5, any_colreg_init(), _OS)]),                         
                        RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(TS3, any_colreg_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS4),
                            RelationDesc(TS5, any_colreg_init(), _OS)]),
                        RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS3),
                            RelationDesc(TS4, any_colreg_init(), _OS),
                            RelationDesc(TS5, any_colreg_init(), _OS)]),
                        RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(TS3, any_colreg_init(), _OS),
                            RelationDesc(TS4, any_colreg_init(), _OS),
                            RelationDesc(TS5, any_colreg_init(), _OS)])])    
]  