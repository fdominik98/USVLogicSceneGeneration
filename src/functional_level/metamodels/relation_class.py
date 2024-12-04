import copy
from typing import List
from functional_level.metamodels.vessel_class import OS, VesselClass
from logical_level.models.relation_types import RelationType


class RelationClass():
    def __init__(self, vd1 : VesselClass, relation_types : List[RelationType], vd2 : VesselClass) -> None:
        self.relation_types = sorted(relation_types, key=lambda x: (str(type(x)), x.negated) )
        if self.all_bidir():
            self.vd1 = min([vd1, vd2], key=lambda x: x.id)
            self.vd2 = max([vd1, vd2], key=lambda x: x.id)
        else:
            self.vd1 = vd1
            self.vd2 = vd2
        
    def __repr__(self) -> str:
        return f'{self.vd1.id}-({", ".join([r.name for r in self.relation_types])})->{self.vd2.id}'
    
    def all_bidir(self):
        return all(rel.is_bidir() for rel in self.relation_types)
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RelationClass):
            return False

        if not self.all_bidir():
            if not (self.vd1 == value.vd1 and self.vd2 == value.vd2):
                return False
        else:
            if not ((self.vd1 == value.vd1 and self.vd2 == value.vd2) or (self.vd1 == value.vd2 and self.vd2 == value.vd1)):
                return False

        if len(self.relation_types) != len(value.relation_types):
            return False
        for rel1, rel2 in zip(self.relation_types, value.relation_types):
            if type(rel1) != type(rel2) or rel1.negated != rel2.negated:
                return False

        return True
    
    def __hash__(self):
        # Combine attributes into a tuple for a unique hash
        return hash((self.vd1, self.vd2) + tuple([(type(rel), rel.negated) for rel in self.relation_types]) + ('desc',))
        
        
class RelationClassClause():
    def __init__(self, relation_descs : List[RelationClass]) -> None:
        self.relation_descs = sorted(set(relation_descs), key=lambda x: hash(x))
        
    def append(self, rel_desc : RelationClass):
        if rel_desc in self.relation_descs:
            return
        self.relation_descs.append(rel_desc)
        self.sort()
        
    def sort(self):
        self.relation_descs = sorted(self.relation_descs, key=lambda x: hash(x))
        
    def __repr__(self) -> str:
        return ', '.join([relation_desc.__repr__() for relation_desc in self.relation_descs])
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RelationClassClause):
            return False

        if len(self.relation_descs) != len(value.relation_descs):
            return False
        for desc1, desc2 in zip(self.relation_descs, value.relation_descs):
            if desc1 != desc2:
                return False

        return True
    
    def get_asymmetric_clause(self):
        self_copy = copy.deepcopy(self)
        for rel_desc in self_copy.relation_descs:
            rel_desc.vd1.id = 0 if isinstance(rel_desc.vd1, OS) else 1
            rel_desc.vd2.id = 0 if isinstance(rel_desc.vd2, OS) else 1
        self_copy.sort()
        return self_copy
    
    def remove_non_ego_ralations(self):
        self.relation_descs = [x for x in self.relation_descs if x.vd1.is_os() or x.vd2.is_os()]
        self.sort()
    
    def __hash__(self):
        # Combine attributes into a tuple for a unique hash
        return hash(tuple([desc for desc in self.relation_descs]) + ('desc',))