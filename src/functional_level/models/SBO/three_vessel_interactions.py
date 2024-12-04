from functional_level.models.model_utils import _OS, TS1, TS2
from functional_level.metamodels.functional_scenario import SBOEnvironmentDesc
from functional_level.metamodels.relation_class import RelationClass
from logical_level.models.relation_types import any_colreg_init, overtaking_or_crossing_init

three_vessel_interactions = [
        SBOEnvironmentDesc(1, [_OS, TS1, TS2],
                        [RelationClass(_OS, any_colreg_init(), TS1),
                        RelationClass(TS2, overtaking_or_crossing_init(), _OS)])    
]  

