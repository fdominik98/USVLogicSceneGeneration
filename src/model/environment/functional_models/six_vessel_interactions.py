from model.vessel import VesselDesc
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.relation_types import crossing_init, head_on_init, overtaking_init
from model.relation import RelationDesc


OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS3 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS4 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS5 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)


six_vessel_interactions = [
        USVEnvironmentDesc('six_vessel_1',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [crossing_init()], OS),
                RelationDesc(OS, [head_on_init()], TS2),
                RelationDesc(TS3, [head_on_init()], OS),
                RelationDesc(OS, [overtaking_init()], TS4),
                RelationDesc(OS, [head_on_init()], TS5)]),
    
        USVEnvironmentDesc('six_vessel_2',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(OS, [overtaking_init()], TS1),
                RelationDesc(OS, [head_on_init()], TS2),
                RelationDesc(TS3, [crossing_init()], OS),
                RelationDesc(OS, [crossing_init()], TS5),
                RelationDesc(TS4, [head_on_init()], OS),
                RelationDesc(OS, [crossing_init()], TS5)]),
        
        USVEnvironmentDesc('six_vessel_3',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [crossing_init()], OS),
                RelationDesc(OS, [crossing_init()], TS2),
                RelationDesc(TS3, [head_on_init()], OS),
                RelationDesc(OS, [head_on_init()], TS4),
                RelationDesc(TS5, [head_on_init()], OS)]),
        
        USVEnvironmentDesc('six_vessel_4',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [overtaking_init()], OS),
                RelationDesc(OS, [overtaking_init()], TS2),
                RelationDesc(TS3, [crossing_init()], OS),
                RelationDesc(OS, [crossing_init()], TS4),
                RelationDesc(TS5, [crossing_init()], OS)]),
        
        USVEnvironmentDesc('six_vessel_5',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [crossing_init()], OS),
                RelationDesc(OS, [head_on_init()], TS2),
                RelationDesc(TS3, [head_on_init()], OS),
                RelationDesc(OS, [crossing_init()], TS4),
                RelationDesc(TS5, [crossing_init()], OS)]),
        
        USVEnvironmentDesc('six_vessel_6',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(OS, [crossing_init()], TS1),
                RelationDesc(OS, [crossing_init()], TS2),
                RelationDesc(TS3, [crossing_init()], OS),
                RelationDesc(OS, [crossing_init()], TS4),
                RelationDesc(TS5, [head_on_init()], OS)]),
        
        USVEnvironmentDesc('six_vessel_7',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [overtaking_init()], OS),
                RelationDesc(OS, [overtaking_init()], TS2),
                RelationDesc(OS, [overtaking_init()], TS3),
                RelationDesc(OS, [crossing_init()], TS4),
                RelationDesc(OS, [overtaking_init()], TS5)]),
        
         USVEnvironmentDesc('six_vessel_8',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [overtaking_init()], OS),
                RelationDesc(TS2, [crossing_init()], OS),
                RelationDesc(OS, [overtaking_init()], TS3),
                RelationDesc(TS4, [overtaking_init()], OS),
                RelationDesc(TS5, [overtaking_init()], OS)]),
         
         USVEnvironmentDesc('six_vessel_9',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [head_on_init()], OS),
                RelationDesc(TS2, [head_on_init()], OS),
                RelationDesc(OS, [head_on_init()], TS3),
                RelationDesc(TS4, [overtaking_init()], OS),
                RelationDesc(TS5, [crossing_init()], OS)]),
         
         USVEnvironmentDesc('six_vessel_10',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [crossing_init()], OS),
                RelationDesc(TS2, [head_on_init()], OS),
                RelationDesc(TS3, [crossing_init()], OS),
                RelationDesc(OS, [crossing_init()], TS4),
                RelationDesc(TS5, [head_on_init()], OS)]),
]   
