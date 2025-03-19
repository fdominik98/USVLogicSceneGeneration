import re
from typing import List
from functional_level.metamodels.functional_scenario import FunctionalScenario
from functional_level.models.functional_scenario_builder import FunctionalScenarioBuilder
from utils.file_system_utils import ASSET_FOLDER, get_all_file_paths


class ModelParser():
    FUNCTIONAL_MODELS_PATH_ALL = f'{ASSET_FOLDER}/functional_models/all'
    FUNCTIONAL_MODELS_PATH_AMBIGUOUS = f'{ASSET_FOLDER}/functional_models/ambiguous'
    
    scenario_path_map = {
        (2, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/2vessel_0obstacle_scenarios',
        (2, 1) : f'{FUNCTIONAL_MODELS_PATH_ALL}/2vessel_1obstacle_scenarios',
        (3, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/3vessel_0obstacle_scenarios',
        (4, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/4vessel_0obstacle_scenarios',
        (5, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/5vessel_0obstacle_scenarios',
        (6, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/6vessel_0obstacle_scenarios'
    }
    
    ambiguous_scenario_path_map = {
        (2, 0) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/2vessel_0obstacle_scenarios',
        (2, 1) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/2vessel_1obstacle_scenarios',
        (3, 0) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/3vessel_0obstacle_scenarios',
        (4, 0) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/4vessel_0obstacle_scenarios',
        (5, 0) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/5vessel_0obstacle_scenarios',
        (6, 0) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/6vessel_0obstacle_scenarios'
    }
    
    @staticmethod
    def parse_problem(problem : str) -> FunctionalScenario:
        cropped_problem = problem.split('declare')[1]
        builder = FunctionalScenarioBuilder()

        # Parse object declarations
        object_pattern = r"(\bOS|\bTS|\bStaticObstacle)\((\w+)\)\."
        for obj_type, obj_name in re.findall(object_pattern, cropped_problem):
            if obj_type == "OS":
                builder.add_new_os(obj_name)
            elif obj_type == "TS":
                builder.add_new_ts(obj_name)
            elif obj_type == "StaticObstacle":
                builder.add_new_obstacle(obj_name)
            else:
                raise ValueError(f"Unknown object type: {obj_type}")

        # Parse relationships
        relationship_patterns = {
            "headOn": lambda o1, o2: builder.add_head_on(o1, o2),
            "overtakingToPort": lambda o1, o2: builder.add_overtaking_to_port(o1, o2),
            "overtakingToStarboard": lambda o1, o2: builder.add_overtaking_to_starboard(o1, o2),
            "crossingFromPort": lambda o1, o2: builder.add_crossing_from_port(o1, o2),
            "atDangerousHeadOnSectorOf" : lambda o1, o2: builder.add_at_dangerous_head_on_sector_of(o1, o2),
            "vesselType" : lambda o1, o2: builder.vessel_type_interpretation.add(o1, o2),
            "staticObstacleType" : lambda o1, o2: builder.static_obstacle_type_interpretation.add(o1, o2),
        }
        for rel_type, assertion in relationship_patterns.items():
            rel_pattern = fr"{rel_type}\((\w+), (\w+)\)\."
            for o1, o2 in re.findall(rel_pattern, cropped_problem):
                if o1 in builder.objects and o2 in builder.objects:
                    assertion(builder.objects[o1], builder.objects[o2])
                    
        return builder.build()
    
    
    @staticmethod
    def load_problem_from_file(file_path : str) -> str:
        with open(file_path, 'r') as file:
            return file.read()
     
    @staticmethod   
    def __load_functional_scenarios(dir : str) -> List[FunctionalScenario]:
        return [ModelParser.parse_problem(ModelParser.load_problem_from_file(path)) for path in get_all_file_paths(dir, 'problem')]
    
    @staticmethod
    def load_functional_scenarios(vessel_number : int, obstacle_number : int) -> List[FunctionalScenario]:
        return ModelParser.__load_functional_scenarios(ModelParser.scenario_path_map[(vessel_number, obstacle_number)])
    
    @staticmethod
    def load_ambiguous_functional_scenarios(vessel_number : int, obstacle_number : int) -> List[FunctionalScenario]:
        return ModelParser.__load_functional_scenarios(ModelParser.ambiguous_scenario_path_map[(vessel_number, obstacle_number)])
    
  
