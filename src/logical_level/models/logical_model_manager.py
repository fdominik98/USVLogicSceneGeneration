import itertools
from typing import List
from logical_level.mapping.instance_initializer import RandomInstanceInitializer
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from logical_level.models.actor_variable import OSVariable, TSVariable
from logical_level.models.logical_scenario import LogicalScenario
from logical_level.models.relation_constraints_concept.composites import RelationConstrTerm
from logical_level.models.relation_constraints_concept.predicates import OutVisOrMayNotCollide, AtVisAndMayCollide

class LogicalModelManager():
    __scenario_cache_map = {
        2 : None,
        3 : None,
        4 : None,
        5 : None,
        6 : None
    }
    
        
    @classmethod
    def get_x_vessel_scenarios(cls, vessel_number) -> List[LogicalScenario]:
        if cls.__scenario_cache_map[vessel_number] is not None:
            return [cls.__scenario_cache_map[vessel_number]]
        
        os = OSVariable(0)
        ts_vessels = [TSVariable(i) for i in range(1, vessel_number)]
        actor_variables = [os] + ts_vessels
        relation_constr_exprs = set([OutVisOrMayNotCollide(v1, v2) for v1, v2 in itertools.combinations(ts_vessels, 2)] + 
        [AtVisAndMayCollide(os, ts) for ts in ts_vessels])
        
        cls.__scenario_cache_map[vessel_number] = LogicalScenario(LogicalScenarioBuilder.get_initializer(RandomInstanceInitializer.name, actor_variables),
                        RelationConstrTerm(relation_constr_exprs),
                        *LogicalScenarioBuilder.get_bounds(actor_variables))
        
        return [cls.__scenario_cache_map[vessel_number]]
        