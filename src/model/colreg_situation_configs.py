from model.colreg_situation import CrossingFromPort, HeadOn, Overtake
from model.colreg_situation_config import ColregSituationConfig
from model.usv_environment_config import USVEnvironmentConfig
from model.usv_config import range_vis


usv_environment_configs : dict[str, USVEnvironmentConfig] = {
    'overtaking_and_crossing' : USVEnvironmentConfig('overtaking_and_crossing',
                                                     [50.0, 50.0, 50.0],
                                                     [ColregSituationConfig(0, CrossingFromPort, 1, range_vis),
                                                      ColregSituationConfig(2, Overtake, 0, range_vis)]),
    
    'two_way_crossing' : USVEnvironmentConfig('two_way_crossing',
                                              [50.0, 50.0, 50.0],
                                              [ColregSituationConfig(0, CrossingFromPort, 1, range_vis),
                                               ColregSituationConfig(2, CrossingFromPort, 0, range_vis)]),
    
    'crossing_and_head_on' : USVEnvironmentConfig('crossing_and_head_on',
                                                  [50.0, 50.0, 50.0],
                                                  [ColregSituationConfig(0, HeadOn, 1, range_vis),
                                                   ColregSituationConfig(2, CrossingFromPort, 0, range_vis)]),

    'overtaking_and_head_on' : USVEnvironmentConfig('overtaking_and_head_on',
                                                    [50.0, 50.0, 50.0],
                                                    [ColregSituationConfig(0, HeadOn, 1, range_vis),
                                                     ColregSituationConfig(2, Overtake, 0, range_vis)]),
    
    'two_way_overtaking' : USVEnvironmentConfig('two_way_overtaking',
                                                [50.0, 50.0, 50.0],
                                                [ColregSituationConfig(0, Overtake, 1, range_vis),
                                                 ColregSituationConfig(2, Overtake, 0, range_vis)]),
    
    'two_way_overtaking_and_crossing' : USVEnvironmentConfig('two_way_overtaking_and_crossing',
                                                             [50.0, 50.0, 50.0, 50.0],
                                                             [ColregSituationConfig(0, Overtake, 1, range_vis),
                                                              ColregSituationConfig(2, Overtake, 0, range_vis),
                                                              ColregSituationConfig(3, CrossingFromPort, 0, range_vis)]),
    
    'six_vessel_colreg_scenario' : USVEnvironmentConfig('six_vessel_colreg_scenario',
                                                             [50.0, 50.0, 50.0, 50.0, 50., 50.0],
                                                              [ColregSituationConfig(2, Overtake, 0, range_vis),
                                                              ColregSituationConfig(3, HeadOn, 0, range_vis),
                                                              ColregSituationConfig(5, CrossingFromPort, 4, range_vis),
                                                              ColregSituationConfig(1, CrossingFromPort, 4, range_vis)]),
    
    'seven_vessel_colreg_scenario_two_island' : USVEnvironmentConfig('seven_vessel_colreg_scenario_two_island',
                                                             [50.0, 50.0, 50.0, 50.0, 50., 50.0, 50.0],
                                                              [ColregSituationConfig(0, CrossingFromPort, 5, range_vis),
                                                              ColregSituationConfig(0, Overtake, 2, range_vis),
                                                              ColregSituationConfig(1, CrossingFromPort, 0, range_vis),
                                                              ColregSituationConfig(6, HeadOn, 1, range_vis),
                                                              ColregSituationConfig(3, Overtake, 4, range_vis)]),
    
    'seven_vessel_colreg_scenario_one_island' : USVEnvironmentConfig('seven_vessel_colreg_scenario_one_island',
                                                             [50.0, 50.0, 50.0, 50.0, 50., 50.0, 50.0],
                                                              [ColregSituationConfig(1, HeadOn, 5, range_vis),
                                                              ColregSituationConfig(5, HeadOn, 3, range_vis),
                                                              ColregSituationConfig(6, Overtake, 2, range_vis),
                                                              ColregSituationConfig(0, HeadOn, 3, range_vis),
                                                              ColregSituationConfig(3, HeadOn, 4, range_vis),
                                                              ColregSituationConfig(6, CrossingFromPort, 0, range_vis)]),
}