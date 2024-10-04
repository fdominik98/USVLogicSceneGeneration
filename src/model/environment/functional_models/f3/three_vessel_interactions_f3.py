from model.vessel import VesselDesc
from model.environment.usv_environment_desc import F3EnvironmentDesc
from model.relation import RelationDesc
from model.relation_types import CrossingBear, HeadOnBear, OvertakingBear, any_colreg_init, crossing_init, OutVisOrNoCollide


OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)

three_vessel_interactions_f3 = [
        F3EnvironmentDesc('three_vessel_1_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [any_colreg_init()], TS1),
                        RelationDesc(TS2, [any_colreg_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), CrossingBear()], TS2)]),
        F3EnvironmentDesc('three_vessel_2_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(OS, [crossing_init()], TS2),
                        RelationDesc(TS1, [OutVisOrNoCollide(), HeadOnBear()], TS2)]),
        F3EnvironmentDesc('three_vessel_3_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(TS2, [any_colreg_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), CrossingBear()], TS2)]),
        F3EnvironmentDesc('three_vessel_4_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(TS1, [OutVisOrNoCollide(), CrossingBear()], TS2)]),
        F3EnvironmentDesc('three_vessel_5_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [any_colreg_init()], TS1),
                        RelationDesc(TS2, [any_colreg_init()], OS),
                        RelationDesc(TS2, [OutVisOrNoCollide(), CrossingBear()], TS1)]),
        
        
        
        F3EnvironmentDesc('three_vessel_6_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [any_colreg_init()], TS1),
                        RelationDesc(TS2, [any_colreg_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), OvertakingBear()], TS2)]),
        F3EnvironmentDesc('three_vessel_7_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [crossing_init()], TS1),
                        RelationDesc(OS, [crossing_init()], TS2),
                        RelationDesc(TS1, [OutVisOrNoCollide(), OvertakingBear()], TS2)]),
        F3EnvironmentDesc('three_vessel_8_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(TS2, [any_colreg_init()], OS),
                        RelationDesc(TS1, [OutVisOrNoCollide(), OvertakingBear()], TS2)]),
        F3EnvironmentDesc('three_vessel_9_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(TS1, [any_colreg_init()], OS),
                        RelationDesc(OS, [any_colreg_init()], TS2),
                        RelationDesc(TS1, [OutVisOrNoCollide(), HeadOnBear()], TS2)]),
        F3EnvironmentDesc('three_vessel_10_f3',
                        [OS, TS1, TS2],
                        [RelationDesc(OS, [any_colreg_init()], TS1),
                        RelationDesc(TS2, [any_colreg_init()], OS),
                        RelationDesc(TS2, [OutVisOrNoCollide(), OvertakingBear()], TS1)]),
]   