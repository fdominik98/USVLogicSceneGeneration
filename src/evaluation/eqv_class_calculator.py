import copy
import itertools
from typing import Dict, List, Set, Tuple
from model.environment.functional_models.usv_env_desc_list import TS3, TS4, TS5
from model.environment.usv_config import OWN_VESSEL_STATES, VARIABLE_NUM
from model.environment.functional_models.model_utils import _OS, TS1, TS2
from model.vessel import Vessel, VesselDesc
from model.relation import Relation, RelationDesc, RelationDescClause
from model.relation_types import RelationType, crossing_init, head_on_init, overtaking_init
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData

class EqvClassCalculator():
    def __init__(self):        
        self.vessels_descs = [_OS, TS1, TS2, TS3, TS4, TS5]
        self.relation_types : List[List[RelationType]] = [crossing_init(), overtaking_init(), head_on_init()]
     
                
    def get_equivalence_classes(self, data : List[EvaluationData]):
        clause_desc_set : Dict[RelationDescClause, int] = {}
        for eval_data in data:
            if eval_data.best_fitness_index > 0.0:
                continue
            _, clause_desc = self.get_clause(eval_data)
            asymmetric_clause = clause_desc.get_asymmetric_clause()
            if asymmetric_clause in clause_desc_set:
                clause_desc_set[asymmetric_clause] += 1
            else:
                clause_desc_set[asymmetric_clause] = 1
        return clause_desc_set
        
    
    def get_clause(self, eval_data : EvaluationData) -> Tuple[List[VesselDesc], RelationDescClause]:
        states = OWN_VESSEL_STATES + eval_data.best_solution
        vessel_descs = self.vessels_descs[:eval_data.vessel_number]
        vessels: Dict[VesselDesc, Vessel] = {}
        for id, vessel_desc in enumerate(vessel_descs):
                vessel = Vessel(vessel_desc)
                vessel.update(states[id * VARIABLE_NUM],
                                states[id * VARIABLE_NUM + 1],
                                states[id * VARIABLE_NUM + 2],
                                states[id * VARIABLE_NUM + 3],
                                states[id * VARIABLE_NUM + 4])
                vessels[vessel_desc] = vessel
            
        combinations = list(itertools.combinations(vessels.keys(), 2))
        clause_desc = RelationDescClause([])
        for id1, id2 in combinations:
            if not id1.is_os() and not id2.is_os():
                continue
            v1 = vessels[id1]
            v2 = vessels[id2]
            rels : Set[Relation] = set()
            for rel_types in self.relation_types:
                rels |= {Relation(v1, copy.deepcopy(rel_types), v2),
                         Relation(v2, copy.deepcopy(rel_types), v1)}
            min_rel = min(rels, key=lambda x: x.penalties_sum)
            if min_rel.penalties_sum == 0.0:
                clause_desc.append(RelationDesc(vd1=min_rel.vessel1.desc,
                                                relation_types=min_rel.relation_types,
                                                vd2=min_rel.vessel2.desc))
        if len(clause_desc.relation_descs) < len(vessels) - 1:
            print('WARNING! Some relations are not recognized')
        return vessel_descs, clause_desc