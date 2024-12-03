from typing import Dict, List, Tuple
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.model.vessel_variable import VesselVariable
from model.relation import Relation, RelationClause
from model.vessel import VesselDesc
from logical_level.mapping.instance_initializer import DeterministicInitializer, InstanceInitializer, LatinHypercubeInitializer, RandomInstanceInitializer
from model.environment.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING
from model.environment.usv_environment import LogicalScenario
from model.environment.usv_environment_desc import MSREnvironmentDesc, USVEnvironmentDesc
from concrete_level.model.concrete_scene import ConcreteScene
from evaluation.eqv_class_calculator import EqvClassCalculator


class LogicalScenarioBuilder():
    def __init__(self) -> None:
        pass
        
    def build_from_functional(self, config : USVEnvironmentDesc, init_method=RandomInstanceInitializer.name) -> LogicalScenario:
        vessels: Dict[VesselDesc, VesselVariable] = {vessel_desc : VesselVariable(vessel_desc) for vessel_desc in config.vessel_descs}
        assignments = Assignments(list(vessels.values()))
        vessel_vars = list(assignments.keys())
        
        for relation_desc_clause in config.relation_desc_clauses:
            clause = RelationClause()
            for relation_desc in relation_desc_clause.relation_descs:
                vd1 = relation_desc.vd1
                vd2 = relation_desc.vd2
                clause.append(Relation(vessels[vd1], relation_desc.relation_types, vessels[vd2]))
            assignments.register_clause(clause)    
       
        xl, xu = self.generate_gene_space(vessel_vars)
        
        return LogicalScenario(config, self.get_initializer(init_method, vessel_vars), assignments, xl, xu)
    
    
        # Attribute generator with different boundaries
    def generate_gene_space(self, vessel_vars : List[VesselVariable]) -> Tuple[List[float], List[float]]:
        xl = [vessel_vars[0].min_length, vessel_vars[0].min_speed]
        xu = [vessel_vars[0].max_length, vessel_vars[0].max_speed]
        for vessel in vessel_vars[1:]:
            xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel.min_length, vessel.min_speed]
            xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel.max_length, vessel.max_speed]
        return xl, xu
    
    
    def build_from_concrete(self, scene : ConcreteScene, init_method=RandomInstanceInitializer.name):
        vessel_descs, clause = EqvClassCalculator().get_clause(scene)
        config = MSREnvironmentDesc(0, vessel_descs, [clause])
        logical_scenario = self.build_from_functional(config, init_method)
        logical_scenario.do_update(scene.population)
        return logical_scenario
        
        
    def get_initializer(self, init_method, vessel_vars : List[VesselVariable]) -> InstanceInitializer:
        if init_method == RandomInstanceInitializer.name: 
            return RandomInstanceInitializer(vessel_vars) 
        elif init_method == DeterministicInitializer.name:
            return DeterministicInitializer(vessel_vars) 
        elif init_method == LatinHypercubeInitializer.name:
            return LatinHypercubeInitializer(vessel_vars) 
        else:
            raise Exception('unknown parameter')