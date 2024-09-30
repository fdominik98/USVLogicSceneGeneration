from model.vessel import VesselDesc
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import CrossingBear, HeadOnBear, OvertakingBear, crossing_init, head_on_init, overtaking_init, OutVisOrNoCollide


OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)

three_vessel_interactions = [
        USVEnvironmentDesc('three_vessel_1',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(TS2, [overtaking_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), CrossingBear()], TS2)]),
        USVEnvironmentDesc('three_vessel_2',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(TS2, [crossing_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), CrossingBear()], TS2)]),
        USVEnvironmentDesc('three_vessel_3',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [head_on_init()], TS1),
                        RelationDesc(TS2, [crossing_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), CrossingBear()], TS2)]),
        USVEnvironmentDesc('three_vessel_4',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [head_on_init()], TS1),
                        RelationDesc(TS2, [overtaking_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), CrossingBear()], TS2)]),
        USVEnvironmentDesc('three_vessel_5',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [overtaking_init()], TS1),
                        RelationDesc(TS2, [overtaking_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), CrossingBear()], TS2)]),
        
        
        
        USVEnvironmentDesc('three_vessel_6',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(TS2, [overtaking_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), OvertakingBear()], TS2)]),

        USVEnvironmentDesc('three_vessel_7',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(TS2, [crossing_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), HeadOnBear()], TS2)]),
        USVEnvironmentDesc('three_vessel_8',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [head_on_init()], TS1),
                        RelationDesc(TS2, [crossing_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), OvertakingBear()], TS2)]),
        USVEnvironmentDesc('three_vessel_9',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [head_on_init()], TS1),
                        RelationDesc(TS2, [overtaking_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), OvertakingBear()], TS2)]),
        USVEnvironmentDesc('three_vessel_10',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [overtaking_init()], TS1),
                        RelationDesc(TS2, [overtaking_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), OvertakingBear()], TS2)]),
]   