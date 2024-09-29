from model.vessel import VesselDesc
from model.colreg_situation import CrossingFromPort, HeadOn, Overtaking
from model.colreg_situation_desc import ColregSituationDesc
from model.environment.usv_environment_desc import USVEnvironmentDesc


OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS3 = VesselDesc(id=3, l=20, b=10, min_speed= 5.0, max_speed=30)

four_vessel_interactions = [
        USVEnvironmentDesc('four_vessel_1',
                        [OS, TS1, TS2, TS3],
                        [ColregSituationDesc(OS, Overtaking, TS3),
                        ColregSituationDesc(TS1, Overtaking, OS),
                        ColregSituationDesc(OS, Overtaking, TS2)]),
        USVEnvironmentDesc('four_vessel_2',
                        [OS, TS1, TS2, TS3],
                        [ColregSituationDesc(OS, Overtaking, TS3),
                        ColregSituationDesc(TS1, CrossingFromPort, OS),
                        ColregSituationDesc(OS, HeadOn, TS2)]),
       
]   