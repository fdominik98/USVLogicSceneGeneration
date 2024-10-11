import itertools
from typing import Dict, List, Set
from model.data_parser import EvalDataParser
from model.environment.functional_models.usv_env_desc_list import TS3, TS4, TS5
from model.environment.usv_config import EPSILON, OWN_VESSEL_STATES, VARIABLE_NUM
from model.environment.functional_models.model_utils import OS, TS1, TS2
from model.vessel import Vessel
from model.relation import Relation, RelationDesc, RelationDescClause
from model.relation_types import OutVisOrNoCollide, RelationType, crossing_init, head_on_init, overtaking_init


clause_desc_set : Dict[RelationDescClause, int] = {}

relation_types : List[List[RelationType]] = [crossing_init(), overtaking_init(), head_on_init()]

dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()

vessels_descs = [OS, TS1, TS2, TS3, TS4, TS5]

for eval_data in eval_datas:
    if eval_data.best_fitness_index >= EPSILON:
        continue
    states = OWN_VESSEL_STATES + eval_data.best_solution
    vessels: Dict[int, Vessel] = {}
    for vessel_desc in vessels_descs[:eval_data.vessel_number]:
        vessel = Vessel(vessel_desc)
        vessel.update(states[vessel.id * VARIABLE_NUM],
                        states[vessel.id * VARIABLE_NUM + 1],
                        states[vessel.id * VARIABLE_NUM + 2],
                        states[vessel.id * VARIABLE_NUM + 3])
        vessels[vessel.id] = vessel
        
    combinations = list(itertools.combinations(vessels.keys(), 2))
    clause_desc = RelationDescClause([])
    for id1, id2 in combinations:
        v1 = vessels[id1]
        v2 = vessels[id2]
        rels : List[Relation] = []
        for rel_types in relation_types:
            rels += [Relation(v1, rel_types, v2), Relation(v2, rel_types, v1)]
        min_rel = min(rels, key=lambda x: x.penalties_sum)
        if min_rel.penalties_sum < EPSILON:
            clause_desc.append(RelationDesc(vd1=min_rel.vessel1.desc, relation_types=min_rel.relation_types, vd2=min_rel.vessel2.desc))
    if clause_desc in clause_desc_set:
        clause_desc_set[clause_desc] += 1
    else:
        clause_desc_set[clause_desc] = 1
    
print(len(clause_desc_set))