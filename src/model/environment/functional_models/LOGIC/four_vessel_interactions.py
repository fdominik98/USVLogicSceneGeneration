from model.environment.functional_models.model_utils import _OS, TS1, TS2, TS3, generate_abstract_models
from model.environment.usv_environment_desc import LOGICEnvironmentDesc
from model.relation import RelationDesc, RelationDescClause
from model.relation_types import any_colreg_init, overtaking_or_crossing_init

four_vessel_interactions = [
        LOGICEnvironmentDesc(1, [_OS, TS1, TS2, TS3],
                        [RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(_OS, any_colreg_init(), TS3)]),                         
                        RelationDescClause(
                            [RelationDesc(_OS, any_colreg_init(), TS1),
                            RelationDesc(TS2, overtaking_or_crossing_init(), _OS),
                            RelationDesc(TS3, any_colreg_init(), _OS)])])    
]  
