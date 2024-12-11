import copy
import itertools
from typing import Dict, List, Set, Tuple
from functional_level.models.usv_env_desc_list import TS3, TS4, TS5
from asv_utils import OWN_VESSEL_STATES, VARIABLE_NUM
from functional_level.models.model_utils import _OS, TS1, TS2
from functional_level.metamodels.vessel_class import VesselClass
from logical_level.models.relation_constraint import RelationConstr
from functional_level.metamodels.relation_class import RelationClass, RelationClassClause
from logical_level.models.constraint_types import ConstraintType, crossing_init, head_on_init, overtaking_init
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from concrete_level.models.concrete_scene import ConcreteScene
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.vessel_variable import VesselVariable

class EqvClassCalculator():
    def __init__(self):        
        self.vessels_descs = [_OS, TS1, TS2, TS3, TS4, TS5]
        self.relation_types : List[List[ConstraintType]] = [crossing_init(), overtaking_init(), head_on_init()]
     
                
    def get_equivalence_classes(self, scenes : List[ConcreteScene]):
        clause_class_set : Dict[RelationClassClause, int] = {}
        for eval_data in data:
            if eval_data.best_fitness_index > 0.0:
                continue
            _, clause_class = self.get_clause(eval_data)
            asymmetric_clause = clause_class.get_asymmetric_clause()
            if asymmetric_clause in clause_class_set:
                clause_class_set[asymmetric_clause] += 1
            else:
                clause_class_set[asymmetric_clause] = 1
        return clause_class_set
    
    def get_functional_model(self, scene : ConcreteScene):        
        _, clause_desc = self.get_clause(scene)
        
    
    def get_clause(self, scene : ConcreteScene) -> Tuple[List[VesselClass], RelationClassClause]:
        vessel_objects = self.vessels_descs[:scene.vessel_num]
        vessels: Dict[VesselClass, VesselVariable] = {vessel_object : VesselVariable(vessel_object) for vessel_object in vessel_objects}
        assignments = Assignments(list(vessels.values()))
        assignments.update_from_population(scene.population)
            
        combinations = list(itertools.combinations(vessels.keys(), 2))
        clause_class = RelationClassClause([])
        for id1, id2 in combinations:
            if not id1.is_os() and not id2.is_os():
                continue
            v1 = vessels[id1]
            v2 = vessels[id2]
            rels : Set[RelationConstr] = set()
            for rel_types in self.relation_types:
                rels |= {RelationConstr(v1, copy.deepcopy(rel_types), v2),
                         RelationConstr(v2, copy.deepcopy(rel_types), v1)}
            min_rel = min(rels, key=lambda x: x.penalties_sum)
            if min_rel.penalties_sum == 0.0:
                clause_class.append(RelationClass(vd1=min_rel.vessel1.functional_class,
                                                relation_types=min_rel.relation_types,
                                                vd2=min_rel.vessel2.functional_class))
        if len(clause_class.relation_descs) < len(vessels) - 1:
            print('WARNING! Some relations are not recognized')
        return vessel_objects, clause_class