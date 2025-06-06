import re
from typing import List
from functional_level.metamodels.functional_scenario import FunctionalScenario
from functional_level.models.functional_scenario_builder import FunctionalScenarioBuilder
from utils.file_system_utils import FUNCTIONAL_MODELS_FOLDER, get_all_file_paths


class ModelParser():
    FUNCTIONAL_MODELS_PATH_ALL = f'{FUNCTIONAL_MODELS_FOLDER}/all'
    FUNCTIONAL_MODELS_PATH_AMBIGUOUS = f'{FUNCTIONAL_MODELS_FOLDER}/ambiguous'
    
    TOTAL_FECS = {(2, 0) : 7,
                  (3, 0) : 28,
                  (4, 0) : 84,
                  (5, 0) : 210,
                  (6, 0) : 462}
    
    scenario_path_map = {
        (2, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/2vessel_0obstacle_scenarios',
        (2, 1) : f'{FUNCTIONAL_MODELS_PATH_ALL}/2vessel_1obstacle_scenarios',
        (3, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/3vessel_0obstacle_scenarios',
        (3, 1) : f'{FUNCTIONAL_MODELS_PATH_ALL}/3vessel_1obstacle_scenarios',
        (4, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/4vessel_0obstacle_scenarios',
        (5, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/5vessel_0obstacle_scenarios',
        (6, 0) : f'{FUNCTIONAL_MODELS_PATH_ALL}/6vessel_0obstacle_scenarios'
    }
    
    ambiguous_scenario_path_map = {
        (2, 0) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/2vessel_0obstacle_scenarios',
        (2, 1) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/2vessel_1obstacle_scenarios',
        (3, 0) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/3vessel_0obstacle_scenarios',
        (3, 1) : f'{FUNCTIONAL_MODELS_PATH_AMBIGUOUS}/3vessel_1obstacle_scenarios',
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
            "vesselType" : lambda o1, o2: builder.add_vessel_type(o1, o2),
            "staticObstacleType" : lambda o1, o2: builder.static_obstacle_type_interpretation.add(o1, o2),
            "inSternSectorOf": lambda o1, o2: builder.in_stern_sector_of_interpretation.add(o1, o2),
            "inPortSideSectorOf": lambda o1, o2: builder.in_port_side_sector_of_interpretation.add(o1, o2),
            "inStarboardSideSectorOf": lambda o1, o2: builder.in_starboard_side_sector_of_interpretation.add(o1, o2),
            "inBowOnSectorOf": lambda o1, o2: builder.in_bow_sector_of_interpretation.add(o1, o2),
            "atVisibilityDistance": lambda o1, o2: builder.at_visibility_distance_interpretation.add(o1, o2),
            "outVisibilityDistance": lambda o1, o2: builder.out_visibility_distance_interpretation.add(o1, o2),
            "inVisibilityDistance": lambda o1, o2: builder.in_visibility_distance_interpretation.add(o1, o2),
            "mayCollide": lambda o1, o2: builder.may_collide_interpretation.add(o1, o2),
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
        scenarios = ModelParser.__load_functional_scenarios(ModelParser.scenario_path_map[(vessel_number, obstacle_number)])
        if len(scenarios) != ModelParser.TOTAL_FECS[(vessel_number, obstacle_number)]:
            raise ValueError(f"Expected {ModelParser.TOTAL_FECS[(vessel_number, obstacle_number)]} scenarios, but found {len(scenarios)} in {ModelParser.scenario_path_map[(vessel_number, obstacle_number)]}")
        return scenarios
    
    @staticmethod
    def load_ambiguous_functional_scenarios(vessel_number : int, obstacle_number : int) -> List[FunctionalScenario]:
        return ModelParser.__load_functional_scenarios(ModelParser.ambiguous_scenario_path_map[(vessel_number, obstacle_number)])
    
  
