from itertools import chain, permutations
from typing import Any, Dict, List, Set, Tuple
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from functional_level.metamodels.functional_scenario import FuncObject, FunctionalScenario
from functional_level.metamodels.interpretation import CrossingFromPortInterpretation, HeadOnInterpretation, OSInterpretation, OvertakingInterpretation, TSInterpretation, VesselClass1Interpretation, VesselClass2Interpretation, VesselClass3Interpretation, VesselClass4Interpretation, VesselClass5Interpretation, VesselClass0Interpretation, VesselClass6Interpretation, VesselClass7Interpretation, VesselClass8Interpretation, VesselInterpretation
from functional_level.models.functional_model_manager import FunctionalModelManager
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from logical_level.mapping.instance_initializer import RandomInstanceInitializer
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from logical_level.models.logical_scenario import LogicalScenario
from concrete_level.models.concrete_scene import ConcreteScene
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.actor_variable import ActorVariable, VesselVariable
from logical_level.models.relation_constraints import RelationConstrComposite, RelationConstrTerm
from logical_level.models.vessel_types import ALL_VESSEL_TYPES

class ConcreteSceneAbstractor():
    
    @staticmethod
    def get_abstractions_from_concrete(scene : ConcreteScene, init_method = RandomInstanceInitializer.name) -> MultiLevelScenario:
        os_interpretation = OSInterpretation()
        ts_interpretation = TSInterpretation()
        head_on_interpretation = HeadOnInterpretation()
        overtaking_interpretation = OvertakingInterpretation()
        crossing_interpretation = CrossingFromPortInterpretation()    
        vessel_class_interpretations : List[VesselInterpretation] = [VesselClass0Interpretation(), VesselClass1Interpretation(),
                                                                     VesselClass2Interpretation(), VesselClass3Interpretation(),
                                                                     VesselClass4Interpretation(), VesselClass5Interpretation(),
                                                                     VesselClass6Interpretation(), VesselClass7Interpretation(),
                                                                     VesselClass8Interpretation()]
        
        vessel_object_map: Dict[ConcreteVessel, FuncObject] = dict()
        vessel_actor_map: Dict[ConcreteVessel, VesselVariable] = dict()
        for vessel in scene.sorted_keys:
            obj = FuncObject(vessel.id)
            vessel_object_map[vessel] = obj
            logical_actor = vessel.logical_variable
            vessel_actor_map[vessel] = logical_actor
            vessel_class_interpretations[ALL_VESSEL_TYPES.index(logical_actor.vessel_type)].add(obj)
            if vessel.is_os:
                os_interpretation.add(obj)
            else:
                ts_interpretation.add(obj)
                
        actor_variables : List[ActorVariable] = list(vessel_actor_map.values())
        
        relation_constr_exprs : Set[RelationConstrComposite] = set()
        
        assignments = Assignments(actor_variables).update_from_individual(scene.individual)
        
        vessel_pairs = list(permutations(scene.actors, 2))
        for v1, v2 in vessel_pairs:
            if not v1.is_os and not v2.is_os:
                continue
            obj1, obj2 = vessel_object_map[v1], vessel_object_map[v2]
            var1, var2 = vessel_actor_map[v1], vessel_actor_map[v2]
            
            # Define terms and their corresponding actions
            exprs_and_assertions : List[Tuple[RelationConstrComposite, RelationConstrComposite, Any]] = [
                #(LogicalScenarioBuilder.get_no_collide_out_vis_clause(var1, var2), None),
                (LogicalScenarioBuilder.get_crossing_term_soft(var1, var2), LogicalScenarioBuilder.get_crossing_term(var1, var2), lambda: crossing_interpretation.add(obj1, obj2)),
                (LogicalScenarioBuilder.get_overtaking_term_soft(var1, var2), LogicalScenarioBuilder.get_overtaking_term(var1, var2), lambda: overtaking_interpretation.add(obj1, obj2)),
                (LogicalScenarioBuilder.get_head_on_term_soft(var1, var2), LogicalScenarioBuilder.get_head_on_term(var1, var2), lambda: head_on_interpretation.add(obj1, obj2)),
            ]
            eval_cache = EvaluationCache(assignments)
            for soft_distance_expr, expr, assertion in exprs_and_assertions:
                penalty = soft_distance_expr._evaluate_penalty(eval_cache)
                if penalty.is_zero:
                    relation_constr_exprs.add(expr)
                    assertion()
                    break
            
        functional_scenario = FunctionalScenario(os_interpretation, ts_interpretation,
                                                 head_on_interpretation, overtaking_interpretation,
                                                 crossing_interpretation, *vessel_class_interpretations)
        
        xl = list(chain.from_iterable([var.lower_bounds for var in actor_variables]))
        xu = list(chain.from_iterable([var.upper_bounds for var in actor_variables]))
        initializer = LogicalScenarioBuilder.get_initializer(init_method, actor_variables)
        logical_scenario = LogicalScenario(initializer, RelationConstrTerm(relation_constr_exprs), xl, xu)  
        
        return MultiLevelScenario(scene, logical_scenario, functional_scenario)
    
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
            else:
                _, count = equivalence_classes[hash]
                equivalence_classes[hash] = (scenario.functional_scenario, count + 1)
        return equivalence_classes, extra_scenarios
    
    @staticmethod 
    def get_ambiguous_equivalence_class_distribution(scenes : List[ConcreteScene], vessel_number) -> Dict[int, Tuple[FunctionalScenario, int]]:
        equivalence_classes : Dict[int, Tuple[FunctionalScenario, int]] = {scenario.shape_hash() : (scenario, 0) for scenario in FunctionalModelManager.get_x_vessel_ambiguous_scenarios(vessel_number)}
        return ConcreteSceneAbstractor.__get_equivalence_class_distribution(equivalence_classes, scenes)[0]
         
    @staticmethod        
    def get_equivalence_class_distribution(scenes : List[ConcreteScene], vessel_number) -> Dict[int, Tuple[FunctionalScenario, int]]:
        equivalence_classes : Dict[int, FunctionalScenario] = {scenario.shape_hash() : (scenario, 0) for scenario in FunctionalModelManager.get_x_vessel_scenarios(vessel_number)}
        return ConcreteSceneAbstractor.__get_equivalence_class_distribution(equivalence_classes, scenes)[0]
    
    @staticmethod        
    def get_unspecified_equivalence_class_distribution(scenes : List[ConcreteScene], vessel_number) -> Dict[int, Tuple[FunctionalScenario, int]]:
        equivalence_classes : Dict[int, FunctionalScenario] = {scenario.shape_hash() : (scenario, 0) for scenario in FunctionalModelManager.get_x_vessel_scenarios(vessel_number)}
        return ConcreteSceneAbstractor.__get_equivalence_class_distribution(equivalence_classes, scenes)[1]
    
    @staticmethod
    def get_abstractions_from_eval(eval_data : EvaluationData) -> MultiLevelScenario:
        return ConcreteSceneAbstractor.get_abstractions_from_concrete(eval_data.best_scene, eval_data.init_method)
    
    