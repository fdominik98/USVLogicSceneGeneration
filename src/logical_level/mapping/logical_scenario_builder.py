from itertools import chain
from typing import Dict, List, Set
from functional_level.metamodels.functional_scenario import FuncObject
from logical_level.models.relation_constraints import AtVis, CrossingBear, HeadOnBear, MayCollide, OutVis, OvertakingBear, RelationConstrClause, RelationConstrTerm
from logical_level.models.actor_variable import ActorVariable, OSVariable, TSVariable, VesselVariable
from logical_level.mapping.instance_initializer import DeterministicInitializer, InstanceInitializer, LatinHypercubeInitializer, RandomInstanceInitializer
from logical_level.models.logical_scenario import LogicalScenario
from functional_level.metamodels.functional_scenario import FunctionalScenario

class LogicalScenarioBuilder():
    def __init__(self) -> None:
        pass
    
    @staticmethod    
    def build_from_functional(functional_scenarios : Set[FunctionalScenario], init_method=RandomInstanceInitializer.name) -> LogicalScenario:        
        object_variable_map: Dict[FunctionalScenario, Dict[FuncObject, ActorVariable]] = {scenario: {} for scenario in functional_scenarios}
        relation_constr_terms : Set[RelationConstrTerm] = set()
        
        for functional_scenario in functional_scenarios:
            for obj in functional_scenario.func_objects:
                if functional_scenario.is_os(obj):
                    var = OSVariable(functional_scenario.id, obj.id)
                elif functional_scenario.is_ts(obj):
                    var = TSVariable(functional_scenario.id, obj.id)
                else:
                    raise ValueError('Neither OS or TS.')
                object_variable_map[functional_scenario][obj] = var
            
            relation_constr_exprs : Set[RelationConstrTerm] = set()
            for o1, o2 in functional_scenario.not_in_colreg_pairs:
                var1, var2 = object_variable_map[functional_scenario][o1], object_variable_map[functional_scenario][o2]
                relation_constr_exprs.add(LogicalScenarioBuilder.get_no_collide_out_vis_clause(var1, var2))
            for o1, o2 in functional_scenario.head_on_interpretation.get_tuples():
                var1, var2 = object_variable_map[functional_scenario][o1], object_variable_map[functional_scenario][o2]
                relation_constr_exprs.add(LogicalScenarioBuilder.get_head_on_term(var1, var2))
            for o1, o2 in functional_scenario.crossing_interpretation.get_tuples():
                var1, var2 = object_variable_map[functional_scenario][o1], object_variable_map[functional_scenario][o2]
                relation_constr_exprs.add(LogicalScenarioBuilder.get_crossing_term(var1, var2))
            for o1, o2 in functional_scenario.overtaking_interpretation.get_tuples():
                var1, var2 = object_variable_map[functional_scenario][o1], object_variable_map[functional_scenario][o2]
                relation_constr_exprs.add(LogicalScenarioBuilder.get_overtaking_term(var1, var2))
            relation_constr_terms.add(RelationConstrTerm(relation_constr_exprs))
        relation_constr_clause = RelationConstrClause(relation_constr_terms)
       
        actor_variables : List[ActorVariable] = sorted([
            actor_var
            for inner_map in object_variable_map.values()
            for actor_var in inner_map.values()
        ], key=lambda x: x.id)
        
        xl = chain.from_iterable([var.lower_bounds for var in actor_variables])
        xu = chain.from_iterable([var.upper_bounds for var in actor_variables])
        return LogicalScenario(LogicalScenarioBuilder.get_initializer(init_method, actor_variables),
                               relation_constr_clause, xl, xu)
    
    @staticmethod    
    def get_initializer(init_method : str, vessel_vars : List[ActorVariable]) -> InstanceInitializer:
        if init_method == RandomInstanceInitializer.name: 
            return RandomInstanceInitializer(vessel_vars) 
        elif init_method == DeterministicInitializer.name:
            return DeterministicInitializer(vessel_vars) 
        elif init_method == LatinHypercubeInitializer.name:
            return LatinHypercubeInitializer(vessel_vars) 
        else:
            raise Exception('unknown parameter')
       
    @staticmethod    
    def get_head_on_term(var1 : VesselVariable, var2 : VesselVariable) -> RelationConstrTerm:
        return RelationConstrTerm({AtVis(var1, var2), HeadOnBear(var1, var2), MayCollide(var1, var2)})
    
    @staticmethod    
    def get_overtaking_term(var1 : VesselVariable, var2 : VesselVariable) -> RelationConstrTerm:
        return RelationConstrTerm({AtVis(var1, var2), OvertakingBear(var1, var2), MayCollide(var1, var2)})
    
    @staticmethod    
    def get_crossing_term(var1 : VesselVariable, var2 : VesselVariable) -> RelationConstrTerm:
        return RelationConstrTerm({AtVis(var1, var2), CrossingBear(var1, var2), MayCollide(var1, var2)})
    
    @staticmethod    
    def get_no_collide_out_vis_clause(var1 : VesselVariable, var2 : VesselVariable) -> RelationConstrClause:
        return RelationConstrClause({OutVis(var1, var2), MayCollide(var1, var2, negated=True)})