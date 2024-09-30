from model.vessel import VesselDesc
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import crossing_init, head_on_init, overtaking_init


OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS3 = VesselDesc(id=3, l=20, b=10, min_speed= 5.0, max_speed=30)

four_vessel_interactions = [
        USVEnvironmentDesc('four_vessel_1',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [overtaking_init()], OS),                        
                        RelationDesc(OS, [overtaking_init()], TS2),
                        RelationDesc(OS, [overtaking_init()], TS3)]),
        USVEnvironmentDesc('four_vessel_2',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [crossing_init()], OS),                        
                        RelationDesc(OS, [head_on_init()], TS2),
                        RelationDesc(OS, [overtaking_init()], TS3),]),
        
        USVEnvironmentDesc('four_vessel_3',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [head_on_init()], TS1),
                        RelationDesc(OS, [overtaking_init()], TS2),
                        RelationDesc(TS3, [crossing_init()], OS)]),
        
        USVEnvironmentDesc('four_vessel_4',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [overtaking_init()], OS),
                        RelationDesc(OS, [head_on_init()], TS2),
                        RelationDesc(OS, [crossing_init()], TS3)]),
        
        USVEnvironmentDesc('four_vessel_5',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(OS, [head_on_init()], TS2),
                        RelationDesc(TS3, [crossing_init()], OS)]),
        
        USVEnvironmentDesc('four_vessel_6',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [crossing_init()], OS),
                        RelationDesc(OS, [crossing_init()], TS2),
                        RelationDesc(OS, [overtaking_init()], TS3)]),
        
        USVEnvironmentDesc('four_vessel_7',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [crossing_init()], OS),
                        RelationDesc(OS, [overtaking_init()], TS2),
                        RelationDesc(OS, [overtaking_init()], TS3)]),
        
         USVEnvironmentDesc('four_vessel_8',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(TS2, [crossing_init()], OS),
                        RelationDesc(OS, [head_on_init()], TS3)]),
         
         USVEnvironmentDesc('four_vessel_9',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [crossing_init()], OS),
                        RelationDesc(OS, [overtaking_init()], TS2),
                        RelationDesc(OS, [crossing_init()], TS3)]),
         
         USVEnvironmentDesc('four_vessel_10',
                        [OS, TS1, TS2, TS3],
                        [RelationDesc(TS1, [head_on_init()], OS),
                        RelationDesc(OS, [head_on_init()], TS2),
                        RelationDesc(TS3, [overtaking_init()], OS)]),
       
       
]   