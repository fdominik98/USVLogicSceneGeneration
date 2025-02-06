from typing import List
from functional_level.metamodels.functional_scenario import FunctionalScenario
from functional_level.models.model_parser import ModelParser

class FunctionalModelManager():
    __scenario_cache_map = {
        2 : None,
        3 : None,
        4 : None,
        5 : None,
        6 : None
    }
    
    __ambiguous_scenario_cache_map = {
        2 : None,
        3 : None,
        4 : None,
        5 : None,
        6 : None
    }   

    
    @classmethod
    def get_x_vessel_ambiguous_scenarios(cls, vessel_number: int) -> List[FunctionalScenario]:
        if cls.__ambiguous_scenario_cache_map[vessel_number] is None:
            cls.__ambiguous_scenario_cache_map[vessel_number] = ModelParser.load_ambiguous_functional_scenarios(vessel_number)
        return cls.__ambiguous_scenario_cache_map[vessel_number]
    
    
    @classmethod
    def get_x_vessel_scenarios(cls, vessel_number: int) -> List[FunctionalScenario]:
        if cls.__scenario_cache_map[vessel_number] is None:
            cls.__scenario_cache_map[vessel_number] = ModelParser.load_functional_scenarios(vessel_number)
        return cls.__scenario_cache_map[vessel_number]
    
    