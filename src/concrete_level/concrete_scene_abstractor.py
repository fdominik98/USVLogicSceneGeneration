from itertools import chain, permutations
from typing import Dict, List, Set, Tuple
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from functional_level.metamodels.functional_scenario import FuncObject, FunctionalScenario
from functional_level.metamodels.interpretation import BinaryInterpretation
from functional_level.models.functional_scenario_builder import FunctionalScenarioBuilder
from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.mapping.instance_initializer import RandomInstanceInitializer
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from logical_level.models.logical_scenario import LogicalScenario
from concrete_level.models.concrete_scene import ConcreteScene
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.actor_variable import ActorVariable
from logical_level.models.relation_constraints_concept.composites import RelationConstrComposite, RelationConstrTerm
from logical_level.models.relation_constraints_concept.literals import AtVis, BinaryLiteral, InHeadOnSectorOf, InVis, MayCollide, OutVis, InPortSideSectorOf, InStarboardSideSectorOf, InSternSectorOf

class ConcreteSceneAbstractor():
    
    __all_scenario_hash_cache : Dict[Tuple[int, int], List[Tuple[int, FunctionalScenario]]] = {}
    __ambiguous_scenario_hash_cache : Dict[Tuple[int, int], List[Tuple[int, FunctionalScenario]]] = {}
    
    @staticmethod
    def get_abstractions_from_concrete(scene : ConcreteScene, init_method = RandomInstanceInitializer.name) -> MultiLevelScenario:
        builder = FunctionalScenarioBuilder()
        
        abstractions : List[Tuple[ActorVariable, FuncObject]] = [actor.create_abstraction(builder) for actor in scene.actors]
                
        actor_variables : List[ActorVariable] = [var for var, _ in abstractions]
        
        relation_constr_exprs : Set[RelationConstrComposite] = set()
        
        assignments = Assignments(actor_variables).update_from_individual(scene.individual)
        eval_cache = EvaluationCache(assignments)
        
        constraint_interpretation_map : List[Tuple[type[BinaryLiteral], BinaryInterpretation]] = [
            (MayCollide, builder.may_collide_interpretation),
            (AtVis, builder.at_visibility_distance_interpretation),
            (OutVis, builder.out_visibility_distance_interpretation),
            (InVis, builder.in_visibility_distance_interpretation),
            (InHeadOnSectorOf, builder.in_head_on_sector_of_interpretation),
            (InPortSideSectorOf, builder.in_port_side_sector_of_interpretation),
            (InStarboardSideSectorOf, builder.in_starboard_side_sector_of_interpretation),
            (InSternSectorOf, builder.in_stern_sector_of_interpretation)
        ]
        
        for (var1, obj1), (var2, obj2) in permutations(abstractions, 2):
            if not var2.is_vessel:
                continue
            
            for Constr, interpretation in constraint_interpretation_map:
                pred = Constr(var1, var2)
                if pred.holds(eval_cache):
                    interpretation.add(obj1, obj2)
                    relation_constr_exprs.add(pred)
            
        functional_scenario = builder.build()
        
        xl = list(chain.from_iterable([var.lower_bounds for var in actor_variables]))
        xu = list(chain.from_iterable([var.upper_bounds for var in actor_variables]))
        initializer = LogicalScenarioBuilder.get_initializer(init_method, actor_variables)
        logical_scenario = LogicalScenario(initializer, RelationConstrTerm(relation_constr_exprs), xl, xu)  
        
        return MultiLevelScenario(scene, logical_scenario, functional_scenario)
    
    @staticmethod
    def get_abstractions_from_eval(eval_data : EvaluationData) -> MultiLevelScenario:
        return ConcreteSceneAbstractor.get_abstractions_from_concrete(eval_data.best_scene, eval_data.init_method)
    
    
    @staticmethod            
    def __get_equivalence_class_distribution(equivalence_classes : Dict[int, Tuple[FunctionalScenario, int]], scenes : List[ConcreteScene]) -> Tuple[Dict[int, Tuple[FunctionalScenario, int]], Dict[int, Tuple[FunctionalScenario, int]]]:
        extra_scenarios : Dict[int, Tuple[FunctionalScenario, int]] = {}
        for scene in scenes:
            scenario = ConcreteSceneAbstractor.get_abstractions_from_concrete(scene)
            hash = scenario.functional_scenario.shape_hash()
            if hash not in equivalence_classes:
                #print('WARNING: new equivalence class found')
                if hash not in extra_scenarios:
                    extra_scenarios[hash] = (scenario.functional_scenario, 1)
                else:
                    _, count = extra_scenarios[hash]
                    extra_scenarios[hash] = (scenario.functional_scenario, count + 1)
                # from concrete_level.models.trajectory_manager import TrajectoryManager
                # from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager
                # ScenarioPlotManager(TrajectoryManager(scenario))
            else:
                _, count = equivalence_classes[hash]
                equivalence_classes[hash] = (scenario.functional_scenario, count + 1)
        return equivalence_classes, extra_scenarios
    
    @staticmethod
    def get_all_equivalence_classes(vessel_number : int, obstacle_number : int):
        actor_number_by_type = (vessel_number, obstacle_number)
        if vessel_number not in ConcreteSceneAbstractor.__all_scenario_hash_cache:
            ConcreteSceneAbstractor.__all_scenario_hash_cache[actor_number_by_type] = [
                (scenario.shape_hash(), scenario) for scenario in
                FunctionalModelManager.get_x_vessel_y_obstacle_scenarios(vessel_number, obstacle_number)]
            
        return {shape_hash : (scenario, 0) for shape_hash, scenario in
                ConcreteSceneAbstractor.__all_scenario_hash_cache[actor_number_by_type]}
    
    @staticmethod
    def get_ambiguous_equivalence_classes(vessel_number : int, obstacle_number : int):
        actor_number_by_type = (vessel_number, obstacle_number)
        if vessel_number not in ConcreteSceneAbstractor.__ambiguous_scenario_hash_cache:
            ConcreteSceneAbstractor.__ambiguous_scenario_hash_cache[actor_number_by_type] = [
                (scenario.shape_hash(), scenario) for scenario in
                FunctionalModelManager.get_x_vessel_y_obstacle_ambiguous_scenarios(vessel_number, obstacle_number)]
            
        return {shape_hash : (scenario, 0) for shape_hash, scenario in
                ConcreteSceneAbstractor.__ambiguous_scenario_hash_cache[actor_number_by_type]}
    
    @staticmethod        
    def get_equivalence_class_distribution(scenes : List[ConcreteScene], vessel_number : int, obstacle_number : int) -> Dict[int, Tuple[FunctionalScenario, int]]:
        equivalence_classes = ConcreteSceneAbstractor.get_all_equivalence_classes(vessel_number, obstacle_number)
        return ConcreteSceneAbstractor.__get_equivalence_class_distribution(equivalence_classes, scenes)[0]
    
    @staticmethod        
    def get_unspecified_equivalence_class_distribution(scenes : List[ConcreteScene], vessel_number : int, obstacle_number : int) -> Dict[int, Tuple[FunctionalScenario, int]]:
        equivalence_classes = ConcreteSceneAbstractor.get_all_equivalence_classes(vessel_number, obstacle_number)
        return ConcreteSceneAbstractor.__get_equivalence_class_distribution(equivalence_classes, scenes)[1]
    
    @staticmethod 
    def get_ambiguous_equivalence_class_distribution(scenes : List[ConcreteScene], vessel_number : int, obstacle_number : int) -> Dict[int, Tuple[FunctionalScenario, int]]:
        equivalence_classes = ConcreteSceneAbstractor.get_ambiguous_equivalence_classes(vessel_number, obstacle_number)
        return ConcreteSceneAbstractor.__get_equivalence_class_distribution(equivalence_classes, scenes)[0]