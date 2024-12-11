import itertools
from typing import List, Set

from functional_level.metamodels.functional_scenario import SBOEnvironmentDesc, MSREnvironmentDesc, FunctionalScenario
from functional_level.metamodels.vessel_class import VesselClass, OS, TS
from functional_level.metamodels.relation_class import RelationClass, RelationClassClause
from logical_level.models.constraint_types import any_colreg_init, crossing_init, head_on_init, overtaking_init, overtaking_or_crossing_init

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

def generate_rel_descs(objects : List[VesselClass], relation_type) -> List[FunctionalScenario]:
    truth_table = itertools.product([0, 1], repeat=len(objects))
    # Generate pairs based on the truth table
    pairs = [
        [[_OS, objects[i]] if comb[i] else [objects[i], _OS] for i in range(len(objects))]
        for comb in truth_table
    ]

    relation_descs : List[List[RelationClass]] = [ ]

    for pair in pairs:
        relation_descs.append([RelationClass(p[0], relation_type(), p[1]) for p in pair])
        
    return relation_descs

def generate_models(config_class : FunctionalScenario.__class__, objects : List[VesselClass], relation_type) -> List[FunctionalScenario]:
    rel_descs_list = generate_rel_descs(objects, relation_type)
    return [config_class(i + 1, [_OS] + objects, rel_descs) for i, rel_descs in enumerate(rel_descs_list)]

def generate_abstract_models(objects : List[VesselClass]) -> List[FunctionalScenario]:
    if len(objects) < 2:
        raise Exception('Only use for 3+ vessel scenarios')
    overtaking_or_crossing = [overtaking_init, crossing_init]
    headon_overtaking_or_crossing = [head_on_init, overtaking_init, crossing_init]
    
    combs = list(itertools.product([True, False], headon_overtaking_or_crossing))
    perms = list(itertools.product(combs, repeat=len(objects[2:])))

    clauses : List[RelationClassClause] = []
    for rel1 in overtaking_or_crossing:
        for rel2 in headon_overtaking_or_crossing:
            for perm in perms:
                clause = RelationClassClause([RelationClass(objects[0], rel1(), _OS),
                                            RelationClass(_OS, rel2(), objects[1])] + 
                                            [RelationClass(o if pos else _OS, 
                                                          rel(), _OS if pos else o)
                                             for o, (pos, rel) in zip(objects[2:], perm)])
                asymmetric_clause = clause.get_asymmetric_clause()
                if asymmetric_clause not in clauses:
                    clauses.append(clause.get_asymmetric_clause())
    
    models : List[MSREnvironmentDesc] = []
    for i, clause in enumerate(clauses):
        rel_descs : List[RelationClass] = []
        for id, rd in enumerate(clause.relation_descs):
            rel_descs.append(RelationClass(_OS if isinstance(rd.vd1, OS) else objects[id],
                                          rd.relation_types,
                                          _OS if isinstance(rd.vd2, OS) else objects[id]))
        
        models.append(MSREnvironmentDesc(i+1, [_OS] + objects, [RelationClassClause(rel_descs)]))
                
                    
    return models



