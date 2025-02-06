import re
from typing import Dict, List

from functional_level.metamodels.functional_object import FuncObject
from functional_level.metamodels.functional_scenario import FunctionalScenario
from functional_level.metamodels.interpretation import CrossingFromPortInterpretation, HeadOnInterpretation, OSInterpretation, OvertakingInterpretation, TSInterpretation
from functional_level.models.object_generator import ObjectGenerator
from utils.file_system_utils import ASSET_FOLDER, get_all_file_paths


class ModelParser():
    FUNCTIONAL_MODELS_PATH_ALL = f'{ASSET_FOLDER}/functional_models/all'
    FUNCTIONAL_MODELS_PATH_AMBIGUOUS = f'{ASSET_FOLDER}/functional_models/ambiguous'
    
    scenario_path_map = {
        2 : f'{FUNCTIONAL_MODELS_PATH_ALL}/2vessel_scenarios',
        3 : f'{FUNCTIONAL_MODELS_PATH_ALL}/3vessel_scenarios',
        4 : f'{FUNCTIONAL_MODELS_PATH_ALL}/4vessel_scenarios',
        5 : f'{FUNCTIONAL_MODELS_PATH_ALL}/5vessel_scenarios',
        6 : f'{FUNCTIONAL_MODELS_PATH_ALL}/6vessel_scenarios'
    }
    
    ambiguous_scenario_path_map = {
        2 : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/2vessel_scenarios',
        3 : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/3vessel_scenarios',
        4 : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/4vessel_scenarios',
        5 : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/5vessel_scenarios',
        6 : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/6vessel_scenarios'
    }
    
    @staticmethod
    def parse_problem(problem : str) -> FunctionalScenario:
        cropped_problem = problem.split('declare')[1]
        
        os_interpretation = OSInterpretation()
        ts_interpretation = TSInterpretation()
        head_on_interpretation = HeadOnInterpretation()
        overtaking_interpretation = OvertakingInterpretation()
        crossing_interpretation = CrossingFromPortInterpretation()        
        
        object_generator = ObjectGenerator()
        objects : Dict[str, FuncObject] = dict()

        # Parse object declarations
        object_pattern = r"(\bOS|\bTS)\((\w+)\)\."
        for obj_type, obj_name in re.findall(object_pattern, cropped_problem):
            obj = object_generator.new_object
            objects[obj_name] = obj
            if obj_type == "OS":
                os_interpretation.add(obj)
            elif obj_type == "TS":
                ts_interpretation.add(obj)

        # Parse relationships
        relationship_patterns = {
            "headOn": lambda o1, o2: head_on_interpretation.add(o1, o2),
            "overtaking": lambda o1, o2: overtaking_interpretation.add(o1, o2),
            "crossingFromPort": lambda o1, o2: crossing_interpretation.add(o1, o2),
        }
        for rel_type, assertion in relationship_patterns.items():
            rel_pattern = fr"{rel_type}\((\w+), (\w+)\)\."
            for o1, o2 in re.findall(rel_pattern, cropped_problem):
                if o1 in objects and o2 in objects:
                    assertion(objects[o1], objects[o2])
        scenario = FunctionalScenario(os_interpretation, ts_interpretation,
                                  head_on_interpretation, overtaking_interpretation,
                                  crossing_interpretation)

        return scenario
    
    
    @staticmethod
    def load_problem_from_file(file_path : str) -> str:
        with open(file_path, 'r') as file:
            return file.read()
     
    @staticmethod   
    def __load_functional_scenarios(dir : str) -> List[FunctionalScenario]:
        return [ModelParser.parse_problem(ModelParser.load_problem_from_file(path)) for path in get_all_file_paths(dir, 'problem')]
    
    @staticmethod
    def load_functional_scenarios(vessel_num : int) -> List[FunctionalScenario]:
        return ModelParser.__load_functional_scenarios(ModelParser.scenario_path_map[vessel_num])
    
    @staticmethod
    def load_ambiguous_functional_scenarios(vessel_num : int) -> List[FunctionalScenario]:
        return ModelParser.__load_functional_scenarios(ModelParser.ambiguous_scenario_path_map[vessel_num])
    
  
