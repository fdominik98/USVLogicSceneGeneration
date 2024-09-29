from typing import Dict
from model.colreg_situation import CrossingFromPort, HeadOn, NoColreg, Overtaking
from model.colreg_situation_desc import ColregSituationDesc
from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.vessel import VesselDesc
from model.environment.functional_models.three_vessel_interactions import three_vessel_interactions
from model.environment.functional_models.four_vessel_interactions import four_vessel_interactions
from model.environment.functional_models.five_vessel_interactions import five_vessel_interactions
from model.environment.functional_models.six_vessel_interactions import six_vessel_interactions

# Length/beam ratio (LBR) = WL/B
# (WL = waterline length; B = maximum beam at the waterline)

# LENGTH-TO-BEAM RATIO (LBR) AND SHIP CATEGORIES
# 
# Ratio       Description                                    Typical Ship Types
# ------------------------------------------------------------------------------------------
# 2-4         Small to midsize planing powerboats            Yachts (6-15m, 15-50 knots)
#             Provides stability and spacious deck area      Small fishing boats (9-15m, 10-25 knots)
#             relative to length, suitable for high-speed    
#             recreational use.
# ------------------------------------------------------------------------------------------
# 3-4         Small to midsize sailboats, motor yachts       Yachts (15-30m, 15-50 knots)
#             Balances stability and speed, suitable         Larger fishing boats (15-30m, 10-25 knots)
#             for both sailing and powerboating.
# ------------------------------------------------------------------------------------------
# 4-6         Large, efficient long-range cruisers           Ferries (30-50m, 15-30 knots)
#             Designed for fuel efficiency and stability,    Small cargo ships (90-150m, 12-20 knots)
#             ideal for ocean passages.
# ------------------------------------------------------------------------------------------
# 6-10        Large freighters, cruising trimarans,          Ferries (50-150m, 15-30 knots)
#             cruising catamarans, and large                 Larger cargo ships (150-180m, 12-20 knots)
#             sailing monohulls                              Icebreakers (60-180m, 10-20 knots)
#             Optimized for long-distance travel, balancing
#             stability and carrying capacity.
# ------------------------------------------------------------------------------------------
# 10-16       Fast-cruising catamarans, trimarans,           Naval ships (variable length, 20-35+ knots)
#             and racing multihulls                          Specialized racing boats
#             High LBR for speed and agility, reducing 
#             drag for competitive sailing.
# ------------------------------------------------------------------------------------------
# Over 16     Racing multihulls                              Specialized racing multihulls
#             Extreme ratios for ultimate speed,             (e.g., America's Cup racers)
#             lightweight, minimal beam to length for 
#             high performance in racing.
# ------------------------------------------------------------------------------------------

# LENGTH AND SPEED CATEGORIES
# ------------------------------------------------------------------------------------------
# Small Ships      6-30 meters         10-50 knots         Yachts, fishing boats
# Medium Ships     30-180 meters       12-30 knots         Ferries, small cargo ships
# Large Ships      180-460+ meters     12-25 knots         Container ships, cruise ships, oil tankers
# Specialized      Variable length     10-35+ knots        Naval ships, icebreakers, racing multihulls
# ------------------------------------------------------------------------------------------




OS = VesselDesc(id=0, l=100, b=30, min_speed= 5.0, max_speed=25)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=30)
TS2 = VesselDesc(id=2, l=100, b=30, min_speed= 5.0, max_speed=25)
TS3 = VesselDesc(id=3, l=100, b=40, min_speed= 5.0, max_speed=25)
TS4 = VesselDesc(id=4, l=50, b=8, min_speed= 5.0, max_speed=30)
TS5 = VesselDesc(id=5, l=50, b=10, min_speed= 5.0, max_speed=30)
TS6 = VesselDesc(id=6, l=100, b=7, min_speed= 5.0, max_speed=25)

OS_BIG = VesselDesc(id=0, l=1000, b=18, min_speed= 3000, max_speed=5000)
TS1_BIG = VesselDesc(id=1, l=1000, b=30, min_speed= 3000, max_speed=5000)
TS2_BIG = VesselDesc(id=2, l=1000, b=30, min_speed= 3000, max_speed=5000)

USV_ENV_DESC_LIST : Dict[str, USVEnvironmentDesc] = {
    'single' : USVEnvironmentDesc('single',
                                       [OS],
                                       []),
    
    'crossing' : USVEnvironmentDesc('crossing',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, CrossingFromPort, TS1)]),
    
    'crossing_big' : USVEnvironmentDesc('crossing_big',
                                       [OS_BIG, TS1_BIG],
                                       [ColregSituationDesc(OS_BIG, CrossingFromPort, TS1_BIG)]),
    
    'nocolreg' : USVEnvironmentDesc('nocolreg',
                                       [OS_BIG, TS1_BIG],
                                       [ColregSituationDesc(OS_BIG, NoColreg, TS1_BIG)]),
    
    'headon' : USVEnvironmentDesc('headon',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, HeadOn, TS1)]),
    
    'headon_big' : USVEnvironmentDesc('headon_big',
                                       [OS_BIG, TS1_BIG],
                                       [ColregSituationDesc(OS_BIG, HeadOn, TS1_BIG)]),
    
    'overtaking' : USVEnvironmentDesc('overtaking',
                                       [OS, TS1],
                                       [ColregSituationDesc(OS, Overtaking, TS1)]),
    
    'overtaking_big' : USVEnvironmentDesc('overtaking_big',
                                       [OS_BIG, TS1_BIG],
                                       [ColregSituationDesc(OS_BIG, Overtaking, TS1_BIG)]),
    
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
    
    'ego_crossing_and_overtaking' : USVEnvironmentDesc('ego_crossing_and_overtaking',
                                                [OS_BIG, TS1_BIG, TS2_BIG],
                                                [ColregSituationDesc(OS_BIG, CrossingFromPort, TS1_BIG),
                                                 ColregSituationDesc(OS_BIG, Overtaking, TS2_BIG)]),
    
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
    
    'six_vessel_colreg_scenario2' : USVEnvironmentDesc('six_vessel_colreg_scenario',
                                                             [OS, TS1, TS2, TS3, TS4, TS5],
                                                              [ColregSituationDesc(OS, Overtaking, TS1),
                                                              ColregSituationDesc(OS, HeadOn, TS2),
                                                              ColregSituationDesc(TS3, CrossingFromPort, OS),
                                                              ColregSituationDesc(OS, CrossingFromPort, TS5),
                                                              ColregSituationDesc(TS4, HeadOn, OS)]),
    
    'seven_vessel_colreg_scenario' : USVEnvironmentDesc('seven_vessel_colreg_scenario',
                                                             [OS, TS1, TS2, TS3, TS4, TS5, TS6],
                                                              [ColregSituationDesc(TS1, CrossingFromPort, OS),
                                                              ColregSituationDesc(OS, HeadOn, TS2),
                                                              ColregSituationDesc(TS3, Overtaking, OS),
                                                              ColregSituationDesc(OS, Overtaking, TS6),
                                                              ColregSituationDesc(TS4, Overtaking, OS),
                                                              ColregSituationDesc(OS, HeadOn, TS5)]),
    
    'seven_vessel_colreg_scenario2' : USVEnvironmentDesc('seven_vessel_colreg_scenario2',
                                                             [OS, TS1, TS2, TS3, TS4, TS5, TS6],
                                                              [ColregSituationDesc(TS3, Overtaking, OS),
                                                              ColregSituationDesc(TS5, HeadOn, OS),
                                                              ColregSituationDesc(TS2, CrossingFromPort, OS),
                                                              ColregSituationDesc(TS4, CrossingFromPort, OS),
                                                              ColregSituationDesc(TS1, HeadOn, OS),
                                                              ColregSituationDesc(TS6, Overtaking, OS)]),
}

for config in three_vessel_interactions + four_vessel_interactions + five_vessel_interactions + six_vessel_interactions:
    USV_ENV_DESC_LIST[config.name] = config