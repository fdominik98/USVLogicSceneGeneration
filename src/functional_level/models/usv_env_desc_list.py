from typing import Dict, List
from functional_level.metamodels.functional_scenario import MSREnvironmentDesc
from functional_level.metamodels.vessel_class import OS, TS
from functional_level.models import SBO
from functional_level.models import MSR
from functional_level.metamodels.relation_class import RelationClass, RelationClassClause
from logical_level.models.constraint_types import crossing_init, head_on_init, overtaking_init

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

# Ambiguous equivalence classes
# 3 vessel : 6
# 4 vessel : 21
# 5 vessel : 50
# 6 vessel : 99
# 7 vessel : 175
# 8 vessel : 286

MSR_EQUIV_CLASSES : dict[int, List[RelationClassClause]] = {
    3 :  [inter.relation_desc_clauses[0] for inter in MSR.three_vessel_interactions],
    4 :  [inter.relation_desc_clauses[0] for inter in MSR.four_vessel_interactions],
    5 :  [inter.relation_desc_clauses[0] for inter in MSR.five_vessel_interactions],
    6 :  [inter.relation_desc_clauses[0] for inter in MSR.six_vessel_interactions]
}
MSR_CONFIGS : dict[int, List[MSREnvironmentDesc]] = {
    3 : MSR.three_vessel_interactions,
    4 : MSR.four_vessel_interactions,
    5 : MSR.five_vessel_interactions,
    6 : MSR.six_vessel_interactions
}

_OS = OS(id=0)
TS1 = TS(id=1)
TS2 = TS(id=2)
TS3 = TS(id=3)
TS4 = TS(id=4)
TS5 = TS(id=5)
TS6 = TS(id=6)

USV_ENV_DESC_LIST : Dict[str, MSREnvironmentDesc] = {}

random_configs = [
    MSREnvironmentDesc('single', [_OS], []),    
    
    MSREnvironmentDesc('crossing', [_OS, TS1], [RelationClass(_OS, crossing_init(), TS1)]),
    
    MSREnvironmentDesc('head_on', [_OS, TS1], [RelationClass(_OS, head_on_init(), TS1)]),
    
    MSREnvironmentDesc('overtaking', [_OS, TS1], [RelationClass(_OS, overtaking_init(), TS1)]),
    
    
    MSREnvironmentDesc('crossing_and_overtaking', [_OS, TS1, TS2],
                    [RelationClass(_OS, overtaking_init(), TS1),
                    RelationClass(TS2, crossing_init(), _OS)]),
    
    MSREnvironmentDesc('overtaking_and_crossing', [_OS, TS1, TS2],
                    [RelationClass(_OS, crossing_init(), TS1),
                    RelationClass(TS2, overtaking_init(), _OS)]),

    MSREnvironmentDesc('two_way_crossing', [_OS, TS1, TS2],
                    [RelationClass(_OS, crossing_init(), TS1),
                    RelationClass(TS2, crossing_init(), _OS)]),
    
    MSREnvironmentDesc('crossing_and_head_on', [_OS, TS1, TS2],
                    [RelationClass(_OS, head_on_init(), TS1),
                    RelationClass(TS2, crossing_init(), _OS)]),

    MSREnvironmentDesc('overtaking_and_head_on', [_OS, TS1, TS2],
                    [RelationClass(_OS, head_on_init(), TS1),
                    RelationClass(TS2, overtaking_init(), _OS)]),
    
    MSREnvironmentDesc('two_way_overtaking', [_OS, TS1, TS2],
                    [RelationClass(_OS, overtaking_init(), TS1),
                    RelationClass(TS2, overtaking_init(), _OS)]),
    

    
    MSREnvironmentDesc('two_way_overtaking_and_crossing',[_OS,TS1, TS2, TS3],
                    [RelationClass(_OS, overtaking_init(), TS1),
                    RelationClass(TS2, overtaking_init(), _OS),
                    RelationClass(TS3, crossing_init(), _OS)]),
    
    MSREnvironmentDesc('overtaking_headon_crossing', [_OS, TS1, TS2, TS3],
                    [RelationClass(TS3, head_on_init(), _OS),
                    RelationClass(_OS, crossing_init(), TS2),
                    RelationClass(TS1, overtaking_init(), _OS)]),
    
    MSREnvironmentDesc('five_vessel_colreg_scenario', [_OS, TS1, TS2, TS3, TS4],
                    [RelationClass(_OS, overtaking_init(), TS3),
                    RelationClass(TS1, crossing_init(), _OS),
                    RelationClass(TS4, head_on_init(), _OS),
                    RelationClass(TS2, crossing_init(), _OS)]),
    
    MSREnvironmentDesc('five_vessel_colreg_scenario_non_ambigious', [_OS, TS1, TS2, TS3, TS4],
                    [RelationClass(_OS, head_on_init(), TS4),
                    RelationClass(_OS, crossing_init(), TS2),
                    RelationClass(TS1, head_on_init(), _OS),
                    RelationClass(TS3, head_on_init(), _OS)]),
    
    MSREnvironmentDesc('six_vessel_colreg_scenario', [_OS, TS1, TS2, TS3, TS4, TS5],
                    [RelationClass(TS1, crossing_init(), _OS),
                    RelationClass(_OS, head_on_init(), TS2),
                    RelationClass(TS3, head_on_init(), _OS),
                    RelationClass(_OS, head_on_init(), TS5),
                    RelationClass(_OS, overtaking_init(), TS4)]),
    
    MSREnvironmentDesc('six_vessel_colreg_scenario', [_OS, TS1, TS2, TS3, TS4, TS5],
                    [RelationClass(_OS, overtaking_init(), TS1),
                    RelationClass(_OS, head_on_init(), TS2),
                    RelationClass(TS3, crossing_init(), _OS),
                    RelationClass(_OS, crossing_init(), TS5),
                    RelationClass(TS4, head_on_init(), _OS)]),
    
    MSREnvironmentDesc('seven_vessel_colreg_scenario', [_OS, TS1, TS2, TS3, TS4, TS5, TS6],
                    [RelationClass(TS1, crossing_init(), _OS),
                    RelationClass(_OS, head_on_init(), TS2),
                    RelationClass(TS3, overtaking_init(), _OS),
                    RelationClass(_OS, overtaking_init(), TS6),
                    RelationClass(TS4, overtaking_init(), _OS),
                    RelationClass(_OS, head_on_init(), TS5)]),
    
    MSREnvironmentDesc('seven_vessel_colreg_scenario2', [_OS, TS1, TS2, TS3, TS4, TS5, TS6],
                    [RelationClass(TS3, overtaking_init(), _OS),
                    RelationClass(TS5, head_on_init(), _OS),
                    RelationClass(TS2, crossing_init(), _OS),
                    RelationClass(TS4, crossing_init(), _OS),
                    RelationClass(TS1, head_on_init(), _OS),
                    RelationClass(TS6, overtaking_init(), _OS)]),
]

for config in random_configs:
    USV_ENV_DESC_LIST[config.id] = config
    USV_ENV_DESC_LIST[config.name] = config

    
for config in MSR.three_vessel_interactions + MSR.four_vessel_interactions + MSR.five_vessel_interactions + MSR.six_vessel_interactions:
    USV_ENV_DESC_LIST[config.name] = config
    
for config in SBO.three_vessel_interactions + SBO.four_vessel_interactions + SBO.five_vessel_interactions + SBO.six_vessel_interactions:
    USV_ENV_DESC_LIST[config.name] = config