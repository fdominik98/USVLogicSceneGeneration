from typing import Dict, List, Set
from logical_level.models.values import Values
from logical_level.models.vessel_variable import VesselVariable
from asv_utils import VARIABLE_NUM

class Assignments(Dict[VesselVariable, Values]):
    def __init__(self, vessel_variables : List[VesselVariable] = [], *args, **kwargs):
        super().__init__({var : None for var in vessel_variables}, *args, **kwargs)
        sorted_items = sorted(self.items(), key=lambda item: item[0].id)
        self.clear()
        self.update(sorted_items)
        
        from logical_level.models.relation_constraint import RelationConstrTerm
        self.registered_clauses : Set[RelationConstrTerm] = set()

    def update_from_population(self, states : List[float]):
        if len(states) != len(self) * VARIABLE_NUM:
            raise Exception("the variable number is insufficient.")
        
        for i, var in enumerate(self.keys()):
            self[var] = Values(x=states[i * VARIABLE_NUM],
                                y=states[i * VARIABLE_NUM + 1],
                                h=states[i * VARIABLE_NUM + 2],
                                l=states[i * VARIABLE_NUM + 3],
                                sp=states[i * VARIABLE_NUM + 4])   
            
        for clause in self.registered_clauses:
            clause.update(self)
            
        self.clause = min(self.registered_clauses, key=lambda clause: clause.penalties_sum)
        self.relations = self.clause.relations  
            
    def register_clause(self, clause):
        self.registered_clauses.add(clause)
        
