from functional_level.models.model_utils import _OS, TS1, TS2, TS3, generate_abstract_models
from functional_level.metamodels.functional_scenario import SBOEnvironmentDesc
from functional_level.metamodels.relation_class import RelationClass, RelationClassClause
from logical_level.models.constraint_types import any_colreg_init, overtaking_or_crossing_init

four_vessel_interactions = [
        SBOEnvironmentDesc(1, [_OS, TS1, TS2, TS3],
                        [RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(_OS, any_colreg_init(), TS3)]),                         
                        RelationClassClause(
                            [RelationClass(_OS, any_colreg_init(), TS1),
                            RelationClass(TS2, overtaking_or_crossing_init(), _OS),
                            RelationClass(TS3, any_colreg_init(), _OS)])])    
]  
