from typing import List
from functional_level.metamodels.functional_scenario import FunctionalScenario
from functional_level.models.model_parser import ModelParser

class FunctionalModelManager():
    __2_vessel_scenarios = None
    __3_vessel_scenarios = None
    __4_vessel_scenarios = None
    __5_vessel_scenarios = None
    __6_vessel_scenarios = None
    
    @classmethod
    def get_2_vessel_scenarios(cls) -> List[FunctionalScenario]:
        if cls.__2_vessel_scenarios is None:
            cls.__2_vessel_scenarios = ModelParser.load_2_vessel_scenarios()
        return cls.__2_vessel_scenarios
    
    @classmethod
    def get_3_vessel_scenarios(cls) -> List[FunctionalScenario]:
        if cls.__3_vessel_scenarios is None:
            cls.__3_vessel_scenarios = ModelParser.load_3_vessel_scenarios()
        return cls.__3_vessel_scenarios
    
    @classmethod
    def get_4_vessel_scenarios(cls) -> List[FunctionalScenario]:
        if cls.__4_vessel_scenarios is None:
            cls.__4_vessel_scenarios = ModelParser.load_4_vessel_scenarios()
        return cls.__4_vessel_scenarios
    
    @classmethod
    def get_5_vessel_scenarios(cls) -> List[FunctionalScenario]:
        if cls.__5_vessel_scenarios is None:
            cls.__5_vessel_scenarios = ModelParser.load_5_vessel_scenarios()
        return cls.__5_vessel_scenarios
    
    @classmethod
    def get_6_vessel_scenarios(cls) -> List[FunctionalScenario]:
        if cls.__6_vessel_scenarios is None:
            cls.__6_vessel_scenarios = ModelParser.load_6_vessel_scenarios()
        return cls.__6_vessel_scenarios
    
    @classmethod
    def get_x_vessel_scenarios(cls, vessel_number: int) -> List[FunctionalScenario]:
        # Use bound methods instead of unbound methods in the map
        scenario_map = {
            3: cls.get_3_vessel_scenarios,
            4: cls.get_4_vessel_scenarios,
            5: cls.get_5_vessel_scenarios,
            6: cls.get_6_vessel_scenarios,
        }
        if vessel_number not in scenario_map:
            raise ValueError(f"Unsupported vessel number: {vessel_number}")
        return scenario_map[vessel_number]()
    
    
    
"""
Ship types:
tanker, MMSI: 413474690 : 93 x 17 m
tanker, MMSI: 412377520 : 146 x 21 m
tanker, MMSI: 413441230 : 82 x 12 m
tanker, MMSI: 413697340 : 96 x 16 m

container, MMSI: 413146000 : 263 x 32 m
container, MMSI: 412713000 : 294 x 32 m
container, MMSI: 212602000 : 259 x 32 m

cargo vessel, MMSI: 413700110 : 159 x 23 m
cargo vessel, MMSI: 412766340 : 179 x 28 m

High Speed Craft, MMSI: 477937400 : 47 x 12 m
High Speed Craft, MMSI: 477937500 : 47 x 12 m
High Speed Craft, MMSI: 477937200 : 47 x 12 m
High Speed Craft, MMSI: 477525000 : 40 x 15 m
High Speed Craft, MMSI: 477385000 :	45 x 12 m

Passenger ship, MMSI: 477995974 : 25 x 8 m
Passenger ship, MMSI: 477995293 : 30 x 8 m

"""
