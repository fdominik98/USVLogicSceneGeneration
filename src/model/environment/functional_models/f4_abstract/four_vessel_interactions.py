from model.environment.usv_environment_desc import F4EnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import crossing_init, head_on_init, overtaking_init
from model.environment.functional_models.model_utils import OS, TS1, TS2, TS3

four_vessel_interactions = [
        F4EnvironmentDesc('four_vessel_1',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [overtaking_init()], OS),                        
                        RelationDesc(OS, [overtaking_init()], TS2),
                        RelationDesc(OS, [overtaking_init()], TS3)]),
        F4EnvironmentDesc('four_vessel_2',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [crossing_init()], OS),                        
                        RelationDesc(OS, [head_on_init()], TS2),
                        RelationDesc(OS, [overtaking_init()], TS3),]),
        
        F4EnvironmentDesc('four_vessel_3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [head_on_init()], TS1),
                        RelationDesc(OS, [overtaking_init()], TS2),
                        RelationDesc(TS3, [crossing_init()], OS)]),
        
        F4EnvironmentDesc('four_vessel_4',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [overtaking_init()], OS),
                        RelationDesc(OS, [head_on_init()], TS2),
                        RelationDesc(OS, [crossing_init()], TS3)]),
        
        F4EnvironmentDesc('four_vessel_5',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(OS, [head_on_init()], TS2),
                        RelationDesc(TS3, [crossing_init()], OS)]),
        
        F4EnvironmentDesc('four_vessel_6',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [crossing_init()], OS),
                        RelationDesc(OS, [crossing_init()], TS2),
                        RelationDesc(OS, [overtaking_init()], TS3)]),
        
        F4EnvironmentDesc('four_vessel_7',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [crossing_init()], OS),
                        RelationDesc(OS, [overtaking_init()], TS2),
                        RelationDesc(OS, [overtaking_init()], TS3)]),
        
         F4EnvironmentDesc('four_vessel_8',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(TS2, [crossing_init()], OS),
                        RelationDesc(OS, [head_on_init()], TS3)]),
         
         F4EnvironmentDesc('four_vessel_9',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [crossing_init()], OS),
                        RelationDesc(OS, [overtaking_init()], TS2),
                        RelationDesc(OS, [crossing_init()], TS3)]),
         
         F4EnvironmentDesc('four_vessel_10',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [head_on_init()], OS),
                        RelationDesc(OS, [head_on_init()], TS2),
                        RelationDesc(TS3, [overtaking_init()], OS)]),
       
       
]   