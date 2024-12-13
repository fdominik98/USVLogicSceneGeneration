from typing import Dict, List, Set, Tuple
from functional_level.metamodels.vessel_class import FuncObject
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.literal import AtVis, CrossingBear, HeadOnBear, MayCollide, OutVis, OvertakingBear, RelationConstrClause, RelationConstrComposite, RelationConstrTerm
from logical_level.models.vessel_variable import VesselVariable
from logical_level.mapping.instance_initializer import DeterministicInitializer, InstanceInitializer, LatinHypercubeInitializer, RandomInstanceInitializer
from asv_utils import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING
from logical_level.models.logical_scenario import LogicalScenario
from functional_level.metamodels.functional_scenario import MSREnvironmentDesc, FunctionalScenario
from concrete_level.models.concrete_scene import ConcreteScene
from evaluation.eqv_class_calculator import EqvClassCalculator


class LogicalScenarioBuilder():
    def __init__(self) -> None:
        pass
        
    def build_from_functional(self, functional_scenario : FunctionalScenario, init_method=RandomInstanceInitializer.name) -> LogicalScenario:
        object_variable_map: Dict[FuncObject, VesselVariable] = {vessel_object : VesselVariable(vessel_object) for vessel_object in functional_scenario.func_objects}
        assignments = Assignments(list(object_variable_map.values()))
        vessel_vars = list(assignments.keys())
        
        relation_constr_exprs : Set[RelationConstrTerm] = set()
        for o1, o2 in functional_scenario.not_in_colreg_pairs:
            var1, var2 = object_variable_map[o1], object_variable_map[o2]
            relation_constr_exprs.add(RelationConstrClause({OutVis(var1, var2), MayCollide(var1, var2, negated=True)}))
        for o1, o2 in functional_scenario.head_on_interpretations.get_tuples():
            var1, var2 = object_variable_map[o1], object_variable_map[o2]
            relation_constr_exprs.add(RelationConstrTerm({AtVis(var1, var2), HeadOnBear(var1, var2), MayCollide(var1, var2)}))
        for o1, o2 in functional_scenario.crossing_interpretations.get_tuples():
            var1, var2 = object_variable_map[o1], object_variable_map[o2]
            relation_constr_exprs.add(RelationConstrTerm({AtVis(var1, var2), CrossingBear(var1, var2), MayCollide(var1, var2)}))
        for o1, o2 in functional_scenario.overtaking_interpretations.get_tuples():
            var1, var2 = object_variable_map[o1], object_variable_map[o2]
            relation_constr_exprs.add(RelationConstrTerm({AtVis(var1, var2), OvertakingBear(var1, var2), MayCollide(var1, var2)}))
        relation_constr_term = RelationConstrTerm(relation_constr_exprs)
       
        xl, xu = self.generate_gene_space(vessel_vars)
        return LogicalScenario(self.get_initializer(init_method, vessel_vars), assignments, xl, xu)
    
        # Attribute generator with different boundaries
    def generate_gene_space(self, vessel_vars : List[VesselVariable]) -> Tuple[List[float], List[float]]:
        xl = [vessel_vars[0].min_length, vessel_vars[0].min_speed]
        xu = [vessel_vars[0].max_length, vessel_vars[0].max_speed]
        for vessel in vessel_vars[1:]:
            xl += [MIN_COORD, MIN_COORD, MIN_HEADING, vessel.min_length, vessel.min_speed]
            xu += [MAX_COORD, MAX_COORD, MAX_HEADING, vessel.max_length, vessel.max_speed]
        return xl, xu
    
    
    def build_from_concrete(self, scene : ConcreteScene, init_method=RandomInstanceInitializer.name):
        vessel_objects, clause = EqvClassCalculator().get_clause(scene)
        config = MSREnvironmentDesc(0, vessel_objects, [clause])
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