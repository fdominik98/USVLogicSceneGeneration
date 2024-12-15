import itertools
from typing import Dict, List, Set, Tuple
from concrete_level.models.concrete_vessel import ConcreteVessel
from functional_level.metamodels.functional_scenario import FuncObject, FunctionalScenario
from functional_level.metamodels.interpretation import CrossingFromPortInterpretation, HeadOnInterpretation, OSInterpretation, OvertakingInterpretation, TSInterpretation
from logical_level.mapping.instance_initializer import RandomInstanceInitializer
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from logical_level.models.logical_scenario import LogicalScenario
from concrete_level.models.concrete_scene import ConcreteScene
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.actor_variable import ActorVariable, OSVariable, TSVariable, VesselVariable
from logical_level.models.relation_constraints import RelationConstrClause, RelationConstrTerm

class ConcreteSceneAbstractor():
    
    @staticmethod
    def get_abstractions_from_concrete(scene : ConcreteScene, init_method = RandomInstanceInitializer.name) -> Tuple[LogicalScenario, FunctionalScenario]:
        os_interpretation = OSInterpretation()
        ts_interpretation = TSInterpretation()
        head_on_interpretation = HeadOnInterpretation()
        overtaking_interpretation = OvertakingInterpretation()
        crossing_interpretation = CrossingFromPortInterpretation()        
        
        vessel_object_map: Dict[ConcreteVessel, FuncObject] = dict()
        vessel_actor_map: Dict[ConcreteVessel, VesselVariable] = dict()
        for vessel in scene.sorted_keys:
            obj = FuncObject(vessel.id)
            vessel_object_map[vessel] = obj
            if vessel.is_os:
                os_interpretation.add(obj)
                vessel_actor_map[vessel] = OSVariable(id=vessel.id)
            else:
                ts_interpretation.add(obj)
                vessel_actor_map[vessel] = TSVariable(id=vessel.id)
        actor_variables : List[ActorVariable] = list(vessel_actor_map.values())
        
        relation_constr_exprs : Set[RelationConstrTerm] = set()
        
        assignments = Assignments(actor_variables)
        assignments.update_from_individual(scene.individual)
        
        vessel_pairs = list(itertools.combinations(scene.actors, 2))
        for v1, v2 in vessel_pairs:
            obj1, obj2 = vessel_object_map[v1], vessel_object_map[v2]
            var1, var2 = vessel_actor_map[v1], vessel_actor_map[v2]
            head_on_term = LogicalScenarioBuilder.get_head_on_term(var1, var2)
            overtaking_term = LogicalScenarioBuilder.get_overtaking_term(var1, var2)
            crossing_term = LogicalScenarioBuilder.get_crossing_term(var1, var2)
            no_collide_out_vis_clause = LogicalScenarioBuilder.get_no_collide_out_vis_clause(var1, var2)
            if head_on_term.evaluate_penalty(assignments).is_zero:
                relation_constr_exprs.add(head_on_term)
                head_on_interpretation.add(obj1, obj2)
            elif overtaking_term.evaluate_penalty(assignments).is_zero:
                overtaking_interpretation.add(obj1, obj2)
                relation_constr_exprs.add(overtaking_term)
            elif crossing_term.evaluate_penalty(assignments).is_zero:
                crossing_interpretation.add(obj1, obj2)
                relation_constr_exprs.add(crossing_term)
            elif no_collide_out_vis_clause.evaluate_penalty(assignments).is_zero:
                relation_constr_exprs.add(no_collide_out_vis_clause)
            else:
                raise Exception('Undefined relation between actors!')
            
        functional_scenario = FunctionalScenario(os_interpretation, ts_interpretation,
                                                 head_on_interpretation, overtaking_interpretation,
                                                 crossing_interpretation)
        
        relation_constr_clause = RelationConstrClause([RelationConstrTerm(relation_constr_exprs)])
        xl = [var.lower_bounds for var in actor_variables]
        xu = [var.upper_bounds for var in actor_variables]
        initializer = LogicalScenarioBuilder.get_initializer(init_method, actor_variables)
        logical_scenario = LogicalScenario(initializer, relation_constr_clause, xl, xu)  
        
        return logical_scenario, functional_scenario
    
    @staticmethod            
    def get_equivalence_classes(self, scenes : List[ConcreteScene]) -> Set[FunctionalScenario]:
        equivalence_classes : Dict[int, FunctionalScenario] = {}
        for scene in scenes:
            _, functional_scenario = ConcreteSceneAbstractor.get_abstractions_from_concrete(scene)
            equivalence_classes[functional_scenario.shape_hash()] = functional_scenario
            
        return set(equivalence_classes.values())