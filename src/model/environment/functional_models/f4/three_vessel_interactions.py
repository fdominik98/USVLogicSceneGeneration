from model.environment.usv_environment_desc import F4EnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import crossing_init, head_on_init, overtaking_init
from model.environment.functional_models.model_utils import OS, TS1, TS2

three_vessel_interactions = [
        F4EnvironmentDesc(1, [OS, TS1, TS2],
                        [RelationDesc(OS, crossing_init(), TS1),
                        RelationDesc(TS2, overtaking_init(), OS)]),
        
        F4EnvironmentDesc(2, [OS, TS1, TS2],
                        [RelationDesc(OS, crossing_init(), TS1),
                        RelationDesc(TS2, crossing_init(), OS)]),
        
        F4EnvironmentDesc(3, [OS, TS1, TS2],
                        [RelationDesc(OS, head_on_init(), TS1),
                        RelationDesc(TS2, crossing_init(), OS)]),
        
        F4EnvironmentDesc(4, [OS, TS1, TS2],
                        [RelationDesc(OS, head_on_init(), TS1),
                        RelationDesc(TS2, overtaking_init(), OS)]),
        
        F4EnvironmentDesc(5, [OS, TS1, TS2],
                        [RelationDesc(OS, overtaking_init(), TS1),
                        RelationDesc(TS2, overtaking_init(), OS)])    
]   