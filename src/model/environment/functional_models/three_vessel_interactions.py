from model.vessel import VesselDesc
from model.colreg_situation import CrossingFromPort, HeadOn, Overtaking
from model.colreg_situation_desc import ColregSituationDesc
from model.environment.usv_environment_desc import USVEnvironmentDesc


OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)

three_vessel_interactions = [
        USVEnvironmentDesc('overtaking_and_crossing',
                        [OS, TS1, TS2],
                        [ColregSituationDesc(OS, CrossingFromPort, TS1),
                        ColregSituationDesc(TS2, Overtaking, OS)]),
        USVEnvironmentDesc('two_way_crossing',
                        [OS, TS1, TS2],
                        [ColregSituationDesc(OS, CrossingFromPort, TS1),
                        ColregSituationDesc(TS2, CrossingFromPort, OS)]),
        USVEnvironmentDesc('crossing_and_head_on',
                        [OS, TS1, TS2],
                        [ColregSituationDesc(OS, HeadOn, TS1),
                        ColregSituationDesc(TS2, CrossingFromPort, OS)]),
        USVEnvironmentDesc('overtaking_and_head_on',
                        [OS, TS1, TS2],
                        [ColregSituationDesc(OS, HeadOn, TS1),
                        ColregSituationDesc(TS2, Overtaking, OS)]),
        USVEnvironmentDesc('two_way_overtaking',
                        [OS, TS1, TS2],
                        [ColregSituationDesc(OS, Overtaking, TS1),
                        ColregSituationDesc(TS2, Overtaking, OS)])
]   