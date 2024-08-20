from model.colreg_situation import CrossingFromPort, HeadOn, Overtaking
from model.colreg_situation_desc import ColregSituationDesc
from model.usv_environment_desc import USVEnvironmentDesc
from model.vessel import VesselDesc

# Yacht:                6-30 meters,        15-50 knots
# Fishing boat:         9-30 meter,         10-25 knots
# Ferries:              30-150 meters,      15-30 knots
# Small Cargo Ships:    90-180 meters,      12-20 knots
# Container Ships:      180-365+ meters,    18-25 knots
# Cruise Ships:         210-365 meters,     18-24 knots
# Oil Tankers:          240-460+ meters,    12-17 knots
# Naval Ships:          ? meters,           20-35+ knots
# Icebreakers:          60-180 meters,      10-20 knots


OS = VesselDesc(id=0, r=100, max_speed=25)
TS1 = VesselDesc(id=1, r=50, max_speed=30)
TS2 = VesselDesc(id=2, r=200, max_speed=20)
TS3 = VesselDesc(id=3, r=300, max_speed=15)
TS4 = VesselDesc(id=4, r=30, max_speed=35)
TS5 = VesselDesc(id=5, r=30, max_speed=35)
TS6 = VesselDesc(id=6, r=20, max_speed=40)

USV_ENV_DESC_LIST : dict[str, USVEnvironmentDesc] = {
    'crossing' : USVEnvironmentDesc('crossing',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, CrossingFromPort, TS1)]),
    
    'headon' : USVEnvironmentDesc('headon',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, HeadOn, TS1)]),
    
    'overtaking' : USVEnvironmentDesc('overtaking',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, Overtaking, TS1)]),
    
    'overtaking_and_crossing' : USVEnvironmentDesc('overtaking_and_crossing',
                                                     [OS, TS1, TS2],
                                                     [ColregSituationDesc(OS, CrossingFromPort, TS1),
                                                      ColregSituationDesc(TS2, Overtaking, OS)]),
    
    'two_way_crossing' : USVEnvironmentDesc('two_way_crossing',
                                              [OS, TS1, TS2],
                                              [ColregSituationDesc(OS, CrossingFromPort, TS1),
                                               ColregSituationDesc(TS2, CrossingFromPort, OS)]),
    
    'crossing_and_head_on' : USVEnvironmentDesc('crossing_and_head_on',
                                                  [OS, TS1, TS2],
                                                  [ColregSituationDesc(OS, HeadOn, TS1),
                                                   ColregSituationDesc(TS2, CrossingFromPort, OS)]),

    'overtaking_and_head_on' : USVEnvironmentDesc('overtaking_and_head_on',
                                                    [OS, TS1, TS2],
                                                    [ColregSituationDesc(OS, HeadOn, TS1),
                                                     ColregSituationDesc(TS2, Overtaking, OS)]),
    
    'two_way_overtaking' : USVEnvironmentDesc('two_way_overtaking',
                                                [OS, TS1, TS2],
                                                [ColregSituationDesc(OS, Overtaking, TS1),
                                                 ColregSituationDesc(TS2, Overtaking, OS)]),
    
    'two_way_overtaking_and_crossing' : USVEnvironmentDesc('two_way_overtaking_and_crossing',
                                                             [OS,TS1, TS2, TS3],
                                                             [ColregSituationDesc(OS, Overtaking, TS1),
                                                              ColregSituationDesc(TS2, Overtaking, OS),
                                                              ColregSituationDesc(TS3, CrossingFromPort, OS)]),
    
    'overtaking_headon_crossing' : USVEnvironmentDesc('overtaking_headon_crossing',
                                                             [OS, TS1, TS2, TS3],
                                                             [ColregSituationDesc(TS3, HeadOn, OS),
                                                              ColregSituationDesc(OS, CrossingFromPort, TS2),
                                                              ColregSituationDesc(TS1, Overtaking, OS)]),
    
    'five_vessel_colreg_scenario' : USVEnvironmentDesc('five_vessel_colreg_scenario',
                                                            [OS, TS1, TS2, TS3, TS4],
                                                            [ColregSituationDesc(OS, Overtaking, TS3),
                                                            ColregSituationDesc(TS1, CrossingFromPort, OS),
                                                            ColregSituationDesc(TS4, HeadOn, OS),
                                                            ColregSituationDesc(TS2, CrossingFromPort, OS)]),
    
    'five_vessel_colreg_scenario_non_ambigious' : USVEnvironmentDesc('five_vessel_colreg_scenario_non_ambigious',
                                                            [OS, TS1, TS2, TS3, TS4],
                                                            [ColregSituationDesc(OS, HeadOn, TS4),
                                                            ColregSituationDesc(OS, CrossingFromPort, TS2),
                                                            ColregSituationDesc(TS1, HeadOn, OS),
                                                            ColregSituationDesc(TS3, HeadOn, OS)]),
    
    'six_vessel_colreg_scenario' : USVEnvironmentDesc('six_vessel_colreg_scenario',
                                                             [OS, TS1, TS2, TS3, TS4, TS5],
                                                              [ColregSituationDesc(TS1, CrossingFromPort, OS),
                                                              ColregSituationDesc(OS, HeadOn, TS2),
                                                              ColregSituationDesc(TS3, HeadOn, OS),
                                                              ColregSituationDesc(OS, HeadOn, TS5),
                                                              ColregSituationDesc(OS, Overtaking, TS4)]),
    
    'seven_vessel_colreg_scenario' : USVEnvironmentDesc('seven_vessel_colreg_scenario',
                                                             [OS, TS1, TS2, TS3, TS4, TS5, TS6],
                                                              [ColregSituationDesc(TS1, CrossingFromPort, OS),
                                                              ColregSituationDesc(OS, HeadOn, TS2),
                                                              ColregSituationDesc(TS3, Overtaking, OS),
                                                              ColregSituationDesc(OS, Overtaking, TS6),
                                                              ColregSituationDesc(TS4, Overtaking, OS),
                                                              ColregSituationDesc(OS, HeadOn, TS5)]),
}