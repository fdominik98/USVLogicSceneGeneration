from functional_level.models.model_utils import _OS, TS1, TS2, TS3, TS4, TS5
from functional_level.metamodels.functional_scenario import SBOEnvironmentDesc
from functional_level.metamodels.relation_class import RelationClass, RelationClassClause
from logical_level.models.constraint_types import any_colreg_init, overtaking_or_crossing_init

six_vessel_interactions = [
        SBOEnvironmentDesc(1, [_OS, TS1, TS2, TS3, TS4, TS5],
                        [RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS3),
                            RelationClass(_OS, any_colreg_init(), TS4),
                            RelationClass(_OS, any_colreg_init(), TS5)]),                         
                        RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(TS3, any_colreg_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS4),
                            RelationClass(_OS, any_colreg_init(), TS5)]),
                        RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS3),
                            RelationClass(TS4, any_colreg_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS5)]),
                        RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(TS3, any_colreg_init(), _OS),
                            RelationClass(TS4, any_colreg_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS5)]),                        
                        RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS3),
                            RelationClass(_OS, any_colreg_init(), TS4),
                            RelationClass(TS5, any_colreg_init(), _OS)]),                         
                        RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(TS3, any_colreg_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS4),
                            RelationClass(TS5, any_colreg_init(), _OS)]),
                        RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS3),
                            RelationClass(TS4, any_colreg_init(), _OS),
                            RelationClass(TS5, any_colreg_init(), _OS)]),
                        RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(TS3, any_colreg_init(), _OS),
                            RelationClass(TS4, any_colreg_init(), _OS),
                            RelationClass(TS5, any_colreg_init(), _OS)])])    
]  