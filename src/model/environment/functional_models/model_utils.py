import itertools
from typing import List, Set

from model.environment.usv_environment_desc import SBOEnvironmentDesc, MSREnvironmentDesc, USVEnvironmentDesc
from model.vessel import VesselDesc, OS, TS
from model.relation import RelationDesc, RelationDescClause
from model.relation_types import any_colreg_init, crossing_init, head_on_init, overtaking_init, overtaking_or_crossing_init

_OS = OS(id=0)
TS1 = TS(id=1)
TS2 = TS(id=2)
TS3 = TS(id=3)
TS4 = TS(id=4)
TS5 = TS(id=5)
TS6 = TS(id=6)
TS7 = TS(id=7)
TS8 = TS(id=8)
TS9 = TS(id=9)
TS10 = TS(id=10)

def generate_rel_descs(objects : List[VesselDesc], relation_type) -> List[USVEnvironmentDesc]:
    truth_table = itertools.product([0, 1], repeat=len(objects))
    # Generate pairs based on the truth table
    pairs = [
        [[_OS, objects[i]] if comb[i] else [objects[i], _OS] for i in range(len(objects))]
        for comb in truth_table
    ]

    relation_descs : List[List[RelationDesc]] = [ ]

    for pair in pairs:
        relation_descs.append([RelationDesc(p[0], relation_type(), p[1]) for p in pair])
        
    return relation_descs

def generate_models(config_class : USVEnvironmentDesc.__class__, objects : List[VesselDesc], relation_type) -> List[USVEnvironmentDesc]:
    rel_descs_list = generate_rel_descs(objects, relation_type)
    return [config_class(i + 1, [_OS] + objects, rel_descs) for i, rel_descs in enumerate(rel_descs_list)]

def generate_abstract_models(objects : List[VesselDesc]) -> List[USVEnvironmentDesc]:
    if len(objects) < 2:
        raise Exception('Only use for 3+ vessel scenarios')
    overtaking_or_crossing = [overtaking_init, crossing_init]
    headon_overtaking_or_crossing = [head_on_init, overtaking_init, crossing_init]
    
    combs = list(itertools.product([True, False], headon_overtaking_or_crossing))
    perms = list(itertools.product(combs, repeat=len(objects[2:])))

    clauses : Set[RelationDescClause] = set()
    for rel1 in overtaking_or_crossing:
        for rel2 in headon_overtaking_or_crossing:
            for perm in perms:
                clause = RelationDescClause([RelationDesc(objects[0], rel1(), _OS),
                                            RelationDesc(_OS, rel2(), objects[1])] + 
                                            [RelationDesc(o if pos else _OS, 
                                                          rel(), _OS if pos else o)
                                             for o, (pos, rel) in zip(objects[2:], perm)])
                clauses.add(clause.get_asymmetric_clause())
    
    models : List[MSREnvironmentDesc] = []
    for i, clause in enumerate(clauses):
        rel_descs : List[RelationDesc] = []
        for id, rd in enumerate(clause.relation_descs):
            rel_descs.append(RelationDesc(_OS if isinstance(rd.vd1, OS) else objects[id],
                                          rd.relation_types,
                                          _OS if isinstance(rd.vd2, OS) else objects[id]))
        
        models.append(MSREnvironmentDesc(i+1, [_OS] + objects, [RelationDescClause(rel_descs)]))
                
                    
    return models



