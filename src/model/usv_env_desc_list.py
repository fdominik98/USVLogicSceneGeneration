from model.colreg_situation import CrossingFromPort, HeadOn, Overtaking
from model.colreg_situation_desc import ColregSituationDesc
from model.usv_environment_desc import USVEnvironmentDesc
from model.usv_config import RANGE_VIS, MAX_SPEED
from model.vessel import VesselDesc

OS = VesselDesc(id=0, r=50, max_speed=MAX_SPEED)
TS1 = VesselDesc(id=1, r=50, max_speed=MAX_SPEED)
TS2 = VesselDesc(id=2, r=50, max_speed=MAX_SPEED)
TS3 = VesselDesc(id=3, r=50, max_speed=MAX_SPEED)
TS4 = VesselDesc(id=4, r=50, max_speed=MAX_SPEED)
TS5 = VesselDesc(id=5, r=50, max_speed=MAX_SPEED)
TS6 = VesselDesc(id=6, r=50, max_speed=MAX_SPEED)

USV_ENV_DESC_LIST : dict[str, USVEnvironmentDesc] = {
    'crossing' : USVEnvironmentDesc('crossing',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, CrossingFromPort, TS1, RANGE_VIS)]),
    
    'headon' : USVEnvironmentDesc('headon',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, HeadOn, TS1, RANGE_VIS)]),
    
    'overtaking' : USVEnvironmentDesc('overtaking',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, Overtaking, TS1, RANGE_VIS)]),
    
    'overtaking_and_crossing' : USVEnvironmentDesc('overtaking_and_crossing',
                                                     [OS, TS1, TS2],
                                                     [ColregSituationDesc(OS, CrossingFromPort, TS1, RANGE_VIS),
                                                      ColregSituationDesc(TS2, Overtaking, OS, RANGE_VIS)]),
    
    'two_way_crossing' : USVEnvironmentDesc('two_way_crossing',
                                              [OS, TS1, TS2],
                                              [ColregSituationDesc(OS, CrossingFromPort, TS1, RANGE_VIS),
                                               ColregSituationDesc(TS2, CrossingFromPort, OS, RANGE_VIS)]),
    
    'crossing_and_head_on' : USVEnvironmentDesc('crossing_and_head_on',
                                                  [OS, TS1, TS2],
                                                  [ColregSituationDesc(OS, HeadOn, TS1, RANGE_VIS),
                                                   ColregSituationDesc(TS2, CrossingFromPort, OS, RANGE_VIS)]),

    'overtaking_and_head_on' : USVEnvironmentDesc('overtaking_and_head_on',
                                                    [OS, TS1, TS2],
                                                    [ColregSituationDesc(OS, HeadOn, TS1, RANGE_VIS),
                                                     ColregSituationDesc(TS2, Overtaking, OS, RANGE_VIS)]),
    
    'two_way_overtaking' : USVEnvironmentDesc('two_way_overtaking',
                                                [OS, TS1, TS2],
                                                [ColregSituationDesc(OS, Overtaking, TS1, RANGE_VIS),
                                                 ColregSituationDesc(TS2, Overtaking, OS, RANGE_VIS)]),
    
    'two_way_overtaking_and_crossing' : USVEnvironmentDesc('two_way_overtaking_and_crossing',
                                                             [OS,TS1, TS2, TS3],
                                                             [ColregSituationDesc(OS, Overtaking, TS1, RANGE_VIS),
                                                              ColregSituationDesc(TS2, Overtaking, OS, RANGE_VIS),
                                                              ColregSituationDesc(TS3, CrossingFromPort, OS, RANGE_VIS)]),
    
    'overtaking_headon_crossing' : USVEnvironmentDesc('overtaking_headon_crossing',
                                                             [OS, TS1, TS2, TS3],
                                                             [ColregSituationDesc(TS3, HeadOn, OS, RANGE_VIS),
                                                              ColregSituationDesc(OS, CrossingFromPort, TS2, RANGE_VIS),
                                                              ColregSituationDesc(TS1, Overtaking, OS, RANGE_VIS)]),
    
    'five_vessel_colreg_scenario' : USVEnvironmentDesc('five_vessel_colreg_scenario',
                                                            [OS, TS1, TS2, TS3, TS4],
                                                            [ColregSituationDesc(OS, Overtaking, TS3, RANGE_VIS),
                                                            ColregSituationDesc(TS1, CrossingFromPort, OS, RANGE_VIS),
                                                            ColregSituationDesc(TS4, HeadOn, OS, RANGE_VIS),
                                                            ColregSituationDesc(TS2, CrossingFromPort, OS, RANGE_VIS)]),
    
    'five_vessel_colreg_scenario_non_ambigious' : USVEnvironmentDesc('five_vessel_colreg_scenario_non_ambigious',
                                                            [OS, TS1, TS2, TS3, TS4],
                                                            [ColregSituationDesc(OS, HeadOn, TS4, RANGE_VIS),
                                                            ColregSituationDesc(OS, CrossingFromPort, TS2, RANGE_VIS),
                                                            ColregSituationDesc(TS1, HeadOn, OS, RANGE_VIS),
                                                            ColregSituationDesc(TS3, HeadOn, OS, RANGE_VIS)]),
    
    'six_vessel_colreg_scenario' : USVEnvironmentDesc('six_vessel_colreg_scenario',
                                                             [OS, TS1, TS2, TS3, TS4, TS5],
                                                              [ColregSituationDesc(TS1, CrossingFromPort, OS, RANGE_VIS),
                                                              ColregSituationDesc(OS, HeadOn, TS2, RANGE_VIS),
                                                              ColregSituationDesc(TS3, HeadOn, OS, RANGE_VIS),
                                                              ColregSituationDesc(OS, HeadOn, TS5, RANGE_VIS),
                                                              ColregSituationDesc(OS, Overtaking, TS4, RANGE_VIS)]),
    
    'seven_vessel_colreg_scenario' : USVEnvironmentDesc('seven_vessel_colreg_scenario',
                                                             [OS, TS1, TS2, TS3, TS4, TS5, TS6],
                                                              [ColregSituationDesc(TS1, CrossingFromPort, OS, RANGE_VIS),
                                                              ColregSituationDesc(OS, HeadOn, TS2, RANGE_VIS),
                                                              ColregSituationDesc(TS3, Overtaking, OS, RANGE_VIS),
                                                              ColregSituationDesc(OS, Overtaking, TS6, RANGE_VIS),
                                                              ColregSituationDesc(TS4, Overtaking, OS, RANGE_VIS),
                                                              ColregSituationDesc(OS, HeadOn, TS5, RANGE_VIS)]),
}