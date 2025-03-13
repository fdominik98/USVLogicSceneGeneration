from itertools import chain
from typing import List, Optional, Tuple
from functional_level.metamodels.functional_object import FuncObject
from logical_level.models.relation_constraints_concept.composites import RelationConstrTerm
from logical_level.models.relation_constraints_concept.predicates import HeadOn, Overtaking, CrossingFromPort, OutVisOrMayNotCollide
from logical_level.models.actor_variable import ActorVariable, OSVariable, TSVariable
from logical_level.mapping.instance_initializer import DeterministicInitializer, InstanceInitializer, LatinHypercubeInitializer, RandomInstanceInitializer
from logical_level.models.logical_scenario import LogicalScenario
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.models.vessel_types import ALL_VESSEL_TYPES, VesselType
from utils.scenario import Scenario

class LogicalScenarioBuilder():  
    @staticmethod    
    def build_from_functional(functional_scenario : FunctionalScenario, init_method=RandomInstanceInitializer.name) -> LogicalScenario:    
        def class_type_map(obj : FuncObject) -> Optional[VesselType]:
            for i, vessel_type in enumerate(ALL_VESSEL_TYPES):
                if functional_scenario.is_vessel_class_x(i, obj):
                    return vessel_type
            raise ValueError('No vessel type found.')
            
        object_variable_map = {
            obj: OSVariable(obj.id, class_type_map(obj)) if functional_scenario.is_os(obj)
            else TSVariable(obj.id, class_type_map(obj)) if functional_scenario.is_ts(obj)
            else ValueError('Neither OS or TS.')
            for obj in functional_scenario.func_objects
        }
        
        # Define interpretations and their corresponding LogicalScenarioBuilder methods
        interpretations = [
            (functional_scenario.not_in_colreg_pairs, OutVisOrMayNotCollide),
            (functional_scenario.head_on_interpretation.get_tuples(), HeadOn),
            (functional_scenario.crossing_from_port_interpretation.get_tuples(), CrossingFromPort),
            (functional_scenario.overtaking_interpretation.get_tuples(), Overtaking),
        ]
        
        # Generate relation constraint expressions
        relation_constr_exprs = {
            predicate(object_variable_map[o1], object_variable_map[o2])
            for tuples, predicate in interpretations
            for o1, o2 in tuples
        }        
       
        actor_variables : List[ActorVariable] = sorted(object_variable_map.values(), key=lambda x: x.id)
        
        return LogicalScenario(LogicalScenarioBuilder.get_initializer(init_method, actor_variables),
                               RelationConstrTerm(relation_constr_exprs), *LogicalScenarioBuilder.get_bounds(actor_variables))
    
    @staticmethod
    def build(scenario : Scenario, init_method : str) -> Tuple[LogicalScenario, Optional[FunctionalScenario]]:
        if isinstance(scenario, FunctionalScenario):
            return (LogicalScenarioBuilder.build_from_functional(scenario, init_method), scenario)
        elif isinstance(scenario, LogicalScenario):
            return (scenario, None)
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
       

    