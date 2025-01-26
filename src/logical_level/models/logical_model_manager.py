import itertools
from typing import List
from logical_level.mapping.instance_initializer import RandomInstanceInitializer
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from logical_level.models.actor_variable import OSVariable, TSVariable
from logical_level.models.logical_scenario import LogicalScenario
from logical_level.models.relation_constraints import RelationConstrTerm


class LogicalModelManager():
    __2_vessel_scenarios = None
    __3_vessel_scenarios = None
    __4_vessel_scenarios = None
    __5_vessel_scenarios = None
    __6_vessel_scenarios = None
    
    @classmethod
    def get_2_vessel_scenarios(cls) -> List[LogicalScenario]:
        if cls.__2_vessel_scenarios is None:
            cls.__2_vessel_scenarios = cls.get_x_vessel_scenarios(2)
        return cls.__2_vessel_scenarios
    
    @classmethod
    def get_3_vessel_scenarios(cls) -> List[LogicalScenario]:
        if cls.__3_vessel_scenarios is None:
            cls.__3_vessel_scenarios = cls.get_x_vessel_scenarios(3)
        return cls.__3_vessel_scenarios
    
    @classmethod
    def get_4_vessel_scenarios(cls) -> List[LogicalScenario]:
        if cls.__4_vessel_scenarios is None:
            cls.__4_vessel_scenarios = cls.get_x_vessel_scenarios(4)
        return cls.__4_vessel_scenarios
    
    @classmethod
    def get_5_vessel_scenarios(cls) -> List[LogicalScenario]:
        if cls.__5_vessel_scenarios is None:
            cls.__5_vessel_scenarios = cls.get_x_vessel_scenarios(5)
        return cls.__5_vessel_scenarios
    
    @classmethod
    def get_6_vessel_scenarios(cls) -> List[LogicalScenario]:
        if cls.__6_vessel_scenarios is None:
            cls.__6_vessel_scenarios = cls.get_x_vessel_scenarios(6)
        return cls.__6_vessel_scenarios
        
    @classmethod
    def get_x_vessel_scenarios(cls, vessel_number) -> List[LogicalScenario]:
        os = OSVariable(0)
        ts_vessels = [TSVariable(i) for i in range(1, vessel_number)]
        actor_variables = [os] + ts_vessels
        relation_constr_exprs = set([LogicalScenarioBuilder.get_no_collide_out_vis_clause(v1, v2) for v1, v2 in itertools.combinations(ts_vessels, 2)] + 
        [LogicalScenarioBuilder.get_at_vis_may_collide_term(os, ts) for ts in ts_vessels])
        return [LogicalScenario(LogicalScenarioBuilder.get_initializer(RandomInstanceInitializer.name, actor_variables),
                        RelationConstrTerm(relation_constr_exprs),
                        *LogicalScenarioBuilder.get_bounds(actor_variables))]
        