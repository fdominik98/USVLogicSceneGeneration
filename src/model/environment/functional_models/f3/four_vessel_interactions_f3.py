from model.vessel import VesselDesc
from model.environment.usv_environment_desc import F4EnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import any_colreg_init, crossing_init, head_on_init, overtaking_init


OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS3 = VesselDesc(id=3, l=20, b=10, min_speed= 5.0, max_speed=30)

four_vessel_interactions = [
        F4EnvironmentDesc('four_vessel_1_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [any_colreg_init()], OS),                        
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(OS, [any_colreg_init()], TS3)]),
        F4EnvironmentDesc('four_vessel_2_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [any_colreg_init()], OS),                        
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(OS, [any_colreg_init()], TS3),]),
        
        F4EnvironmentDesc('four_vessel_3_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [any_colreg_init()], TS1),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(TS3, [any_colreg_init()], OS)]),
        
        F4EnvironmentDesc('four_vessel_4_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(OS, [any_colreg_init()], TS3)]),
        
        F4EnvironmentDesc('four_vessel_5_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [any_colreg_init()], TS1),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(TS3, [any_colreg_init()], OS)]),
        
        F4EnvironmentDesc('four_vessel_6_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(OS, [any_colreg_init()], TS3)]),
        
        F4EnvironmentDesc('four_vessel_7_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(OS, [any_colreg_init()], TS3)]),
        
         F4EnvironmentDesc('four_vessel_8_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [any_colreg_init()], TS1),
                        RelationDesc(TS2, [any_colreg_init()], OS),
                        RelationDesc(OS, [any_colreg_init()], TS3)]),
         
         F4EnvironmentDesc('four_vessel_9_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(OS, [any_colreg_init()], TS3)]),
         
         F4EnvironmentDesc('four_vessel_10_f3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(TS3, [any_colreg_init()], OS)]),
       
       
]   