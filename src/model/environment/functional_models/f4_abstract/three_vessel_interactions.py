from model.environment.functional_models.model_utils import _OS, TS1, TS2
from model.environment.usv_environment_desc import F4AbstractEnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import any_colreg_init, overtaking_or_crossing_init

three_vessel_interactions = [
        F4AbstractEnvironmentDesc(1, [_OS, TS1, TS2],
                        [RelationDesc(_OS, any_colreg_init(), TS1),
                        RelationDesc(TS2, overtaking_or_crossing_init(), _OS)])    
]  

