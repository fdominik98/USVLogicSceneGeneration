import itertools
from typing import List

from model.environment.usv_environment_desc import F4AbstractEnvironmentDesc, USVEnvironmentDesc
from model.vessel import VesselDesc
from model.relation import RelationDesc, RelationDescClause
from model.relation_types import any_colreg_init, overtaking_or_crossing_init

OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS3 = VesselDesc(id=3, l=20, b=10, min_speed= 5.0, max_speed=30)
TS4 = VesselDesc(id=4, l=20, b=10, min_speed= 5.0, max_speed=30)
TS5 = VesselDesc(id=5, l=20, b=10, min_speed= 5.0, max_speed=30)

def generate_rel_descs(objects : List[VesselDesc], relation_type) -> List[USVEnvironmentDesc]:
    truth_table = itertools.product([0, 1], repeat=len(objects))
    # Generate pairs based on the truth table
    pairs = [
        [[OS, objects[i]] if comb[i] else [objects[i], OS] for i in range(len(objects))]
        for comb in truth_table
    ]

    relation_descs : List[List[RelationDesc]] = [ ]

    for pair in pairs:
        relation_descs.append([RelationDesc(p[0], relation_type(), p[1]) for p in pair])
        
    return relation_descs

def generate_models(config_class : USVEnvironmentDesc.__class__, objects : List[VesselDesc], relation_type) -> List[USVEnvironmentDesc]:
    rel_descs_list = generate_rel_descs(objects, relation_type)
    return [config_class(f'{len(objects) + 1}_vessel_{i+1}_{config_class.group}', [OS] + objects, rel_descs) for i, rel_descs in enumerate(rel_descs_list)]

def generate_abstract_models(objects : List[VesselDesc]) -> List[USVEnvironmentDesc]:
    permutations = list(itertools.permutations(objects, 2))

    clauses : List[RelationDescClause] = []
    for perm in permutations:
            rem = [o for o in objects if o not in perm]
            rem_rel_desc_list = generate_rel_descs(rem, any_colreg_init)
            for rem_rel_descs in rem_rel_desc_list:
                    clauses.append(RelationDescClause(rem_rel_descs +
                            [RelationDesc(perm[0], [overtaking_or_crossing_init()], OS)] +
                            [RelationDesc(OS, [any_colreg_init()], perm[1])]))
                    
    return [F4AbstractEnvironmentDesc(f'{len(objects) + 1}_vessel_{F4AbstractEnvironmentDesc.group}', [OS] + objects, clauses)]
