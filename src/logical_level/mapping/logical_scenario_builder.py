from itertools import chain
from typing import List, Tuple, Union
from functional_level.metamodels.functional_object import FuncObject
from logical_level.models.relation_constraints import AtVis, CrossingBear, HeadOnBear, MayCollide, OutVis, OvertakingBear, RelationConstrClause, RelationConstrTerm
from logical_level.models.actor_variable import ActorVariable, OSVariable, TSVariable, VesselVariable
from logical_level.mapping.instance_initializer import DeterministicInitializer, InstanceInitializer, LatinHypercubeInitializer, RandomInstanceInitializer
from logical_level.models.logical_scenario import LogicalScenario
from functional_level.metamodels.functional_scenario import FunctionalScenario
from utils.asv_utils import MAX_LENGTH, MIN_LENGTH
from utils.scenario import Scenario

class LogicalScenarioBuilder():
    
    class_length_ranges = [
        (1, MIN_LENGTH, 50),
        (2, 50, 100),
        (3, 100, 150),
        (4, 150, 200),
        (5, 200, 250),
        (6, 250, 300),
        (7, 300, 350),
        (8, 350, MAX_LENGTH),
    ]
    
    @staticmethod    
    def build_from_functional(functional_scenario : FunctionalScenario, init_method=RandomInstanceInitializer.name) -> LogicalScenario:    
        def class_length_map(obj : FuncObject) -> Tuple[float, float]:
            min_length = MIN_LENGTH
            max_length = MAX_LENGTH
            for cls, cls_min, cls_max in LogicalScenarioBuilder.class_length_ranges:
                if functional_scenario.is_vessel_class_x(cls, obj):
                    min_length = min(min_length, cls_min)
                    max_length = max(max_length, cls_max)
            
            return min_length, max_length
            
        object_variable_map = {
            obj: OSVariable(obj.id, *class_length_map(obj)) if functional_scenario.is_os(obj)
            else TSVariable(obj.id, *class_length_map(obj)) if functional_scenario.is_ts(obj)
            else ValueError('Neither OS or TS.')
            for obj in functional_scenario.func_objects
        }
        
        # Define interpretations and their corresponding LogicalScenarioBuilder methods
        interpretations = [
            (functional_scenario.not_in_colreg_pairs, LogicalScenarioBuilder.get_no_collide_out_vis_clause),
            (functional_scenario.head_on_interpretation.get_tuples(), LogicalScenarioBuilder.get_head_on_term),
            (functional_scenario.crossing_interpretation.get_tuples(), LogicalScenarioBuilder.get_crossing_term),
            (functional_scenario.overtaking_interpretation.get_tuples(), LogicalScenarioBuilder.get_overtaking_term),
        ]
        
        # Generate relation constraint expressions
        relation_constr_exprs = {
            method(
                object_variable_map[o1],
                object_variable_map[o2]
            )
            for tuples, method in interpretations
            for o1, o2 in tuples
        }        
       
        actor_variables : List[ActorVariable] = sorted(object_variable_map.values(), key=lambda x: x.id)
        
        return LogicalScenario(LogicalScenarioBuilder.get_initializer(init_method, actor_variables),
                               RelationConstrTerm(relation_constr_exprs), *LogicalScenarioBuilder.get_bounds(actor_variables))
    
    @staticmethod
    def build(scenario : Scenario, init_method : str) -> LogicalScenario:
        if isinstance(scenario, FunctionalScenario):
            return LogicalScenarioBuilder.build_from_functional(scenario, init_method) 
        elif isinstance(scenario, LogicalScenario):
            return scenario
        else:
            raise ValueError('Insufficient scenario type')
        
    @staticmethod    
    def get_bounds(actor_variables : List[ActorVariable]) -> Tuple[List[float], List[float]]:
        xl = list(chain.from_iterable([var.lower_bounds for var in actor_variables]))
        xu = list(chain.from_iterable([var.upper_bounds for var in actor_variables]))
        return xl, xu
    
    @staticmethod    
    def get_initializer(init_method : str, vessel_vars : List[ActorVariable]) -> InstanceInitializer:
        if init_method == RandomInstanceInitializer.name or init_method == None: 
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
    
    def get_at_vis_may_collide_term(var1 : VesselVariable, var2 : VesselVariable) -> RelationConstrTerm:
        return RelationConstrTerm({AtVis(var1, var2), MayCollide(var1, var2)})
    