from itertools import chain
from typing import Dict, List, Set
from functional_level.metamodels.functional_scenario import FuncObject
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.literal import AtVis, CrossingBear, HeadOnBear, MayCollide, OutVis, OvertakingBear, RelationConstrClause, RelationConstrTerm
from logical_level.models.vessel_variable import ActorVariable, OSVariable, TSVariable
from logical_level.mapping.instance_initializer import DeterministicInitializer, InstanceInitializer, LatinHypercubeInitializer, RandomInstanceInitializer
from logical_level.models.logical_scenario import LogicalScenario
from functional_level.metamodels.functional_scenario import MSREnvironmentDesc, FunctionalScenario
from concrete_level.models.concrete_scene import ConcreteScene
from evaluation.eqv_class_calculator import EqvClassCalculator


class LogicalScenarioBuilder():
    def __init__(self) -> None:
        pass
        
    def build_from_functional(self, functional_scenarios : Set[FunctionalScenario], init_method=RandomInstanceInitializer.name) -> LogicalScenario:        
        object_variable_map: Dict[FunctionalScenario, Dict[FuncObject, ActorVariable]] = {scenario: {} for scenario in functional_scenarios}
        for functional_scenario in functional_scenarios:
            for obj in functional_scenario.func_objects:
                if functional_scenario.is_os(obj):
                    var = OSVariable(functional_scenario.id, obj.id)
                elif functional_scenario.is_ts(obj):
                    var = TSVariable(functional_scenario.id, obj.id)
                else:
                    raise ValueError('Neither OS or TS.')
            object_variable_map[functional_scenario][obj] = var
        
        relation_constr_terms : Set[RelationConstrTerm] = set()
        for functional_scenario in functional_scenarios:
            relation_constr_exprs : Set[RelationConstrTerm] = set()
            for o1, o2 in functional_scenario.not_in_colreg_pairs:
                var1, var2 = object_variable_map[functional_scenario][o1], object_variable_map[functional_scenario][o2]
                relation_constr_exprs.add(RelationConstrClause({OutVis(var1, var2), MayCollide(var1, var2, negated=True)}))
            for o1, o2 in functional_scenario.head_on_interpretations.get_tuples():
                var1, var2 = object_variable_map[functional_scenario][o1], object_variable_map[functional_scenario][o2]
                relation_constr_exprs.add(RelationConstrTerm({AtVis(var1, var2), HeadOnBear(var1, var2), MayCollide(var1, var2)}))
            for o1, o2 in functional_scenario.crossing_interpretations.get_tuples():
                var1, var2 = object_variable_map[functional_scenario][o1], object_variable_map[functional_scenario][o2]
                relation_constr_exprs.add(RelationConstrTerm({AtVis(var1, var2), CrossingBear(var1, var2), MayCollide(var1, var2)}))
            for o1, o2 in functional_scenario.overtaking_interpretations.get_tuples():
                var1, var2 = object_variable_map[functional_scenario][o1], object_variable_map[functional_scenario][o2]
                relation_constr_exprs.add(RelationConstrTerm({AtVis(var1, var2), OvertakingBear(var1, var2), MayCollide(var1, var2)}))
            relation_constr_terms.add(RelationConstrTerm(relation_constr_exprs))
        relation_constr_clause = RelationConstrClause(relation_constr_terms)
       
        actor_variables : List[ActorVariable] = sorted([
            actor_var
            for inner_map in object_variable_map.values()
            for actor_var in inner_map.values()
        ], key=lambda x: (x.scope_id, x.id))
        
        xl = chain.from_iterable([var.lower_bounds for var in actor_variables])
        xu = chain.from_iterable([var.upper_bounds for var in actor_variables])
        return LogicalScenario(self.get_initializer(init_method, actor_variables), relation_constr_clause, xl, xu)
        
    
    def build_from_concrete(self, scene : ConcreteScene, init_method=RandomInstanceInitializer.name):
        vessel_objects, clause = EqvClassCalculator().get_clause(scene)
        config = MSREnvironmentDesc(0, vessel_objects, [clause])
        logical_scenario = self.build_from_functional(config, init_method)
        #logical_scenario.update(scene.population)
        return logical_scenario
        
        
    def get_initializer(self, init_method, vessel_vars : List[ActorVariable]) -> InstanceInitializer:
        if init_method == RandomInstanceInitializer.name: 
            return RandomInstanceInitializer(vessel_vars) 
        elif init_method == DeterministicInitializer.name:
            return DeterministicInitializer(vessel_vars) 
        elif init_method == LatinHypercubeInitializer.name:
            return LatinHypercubeInitializer(vessel_vars) 
        else:
            raise Exception('unknown parameter')