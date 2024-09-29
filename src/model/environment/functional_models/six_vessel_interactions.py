from model.vessel import VesselDesc
from model.colreg_situation import CrossingFromPort, HeadOn, Overtaking
from model.colreg_situation_desc import ColregSituationDesc, RelationDesc
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.relation_types import CROSSING_INIT, HEAD_ON_INIT, OVERTAKING_INIT, IN_VIS


OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS3 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS4 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS5 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)

six_vessel_interactions = [
        USVEnvironmentDesc('six_vessel_1',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [RelationDesc(TS1, [CROSSING_INIT], OS),
                 RelationDesc(OS, [HEAD_ON_INIT], TS2),
                 RelationDesc(TS3, [HEAD_ON_INIT], OS),
                 RelationDesc(OS, [HEAD_ON_INIT], TS4),
                 RelationDesc(OS, [OVERTAKING_INIT], TS5),  
                 
                 RelationDesc(TS1, [IN_VIS], TS2),
                 RelationDesc(TS1, [IN_VIS], TS3),
                 RelationDesc(TS1, [IN_VIS], TS4),
                 RelationDesc(TS1, [IN_VIS], TS5),  
                 
                 RelationDesc(TS2, [IN_VIS], TS3),
                 RelationDesc(TS2, [IN_VIS], TS4),
                 RelationDesc(TS2, [IN_VIS], TS5),  
                 
                 RelationDesc(TS3, [IN_VIS], TS4),
                 RelationDesc(TS3, [IN_VIS], TS5),  
                 
                 RelationDesc(TS4, [IN_VIS], TS5),  
        ]),
]



six_vessel_interactions = [
        USVEnvironmentDesc('six_vessel_1',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [ColregSituationDesc(TS1, CrossingFromPort, OS),
                ColregSituationDesc(OS, HeadOn, TS2),
                ColregSituationDesc(TS3, HeadOn, OS),
                ColregSituationDesc(OS, HeadOn, TS5),
                ColregSituationDesc(OS, Overtaking, TS4)]),
    
        USVEnvironmentDesc('six_vessel_2',
                [OS, TS1, TS2, TS3, TS4, TS5],
                [ColregSituationDesc(OS, Overtaking, TS1),
                ColregSituationDesc(OS, HeadOn, TS2),
                ColregSituationDesc(TS3, CrossingFromPort, OS),
                ColregSituationDesc(OS, CrossingFromPort, TS5),
                ColregSituationDesc(TS4, HeadOn, OS)]),
]   
