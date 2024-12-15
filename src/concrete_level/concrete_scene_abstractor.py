import copy
import itertools
from typing import Dict, List, Set, Tuple
from concrete_level.models.concrete_vessel import ConcreteVessel
from logical_level.mapping.instance_initializer import RandomInstanceInitializer
from logical_level.models.logical_scenario import LogicalScenario
from logical_level.models.relation_constraint import RelationConstr
from concrete_level.models.concrete_scene import ConcreteScene
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.actor_variable import ActorVariable, OSVariable, TSVariable, VesselVariable
from logical_level.models.relation_constraints import AtVis, CrossingBear, HeadOnBear, MayCollide, OutVis, OvertakingBear, RelationConstrClause, RelationConstrTerm

class ConcreteSceneAbstractor():
     
    def get_logical_from_concrete(self, scene : ConcreteScene) -> LogicalScenario:
        vessel_actor_map: Dict[ConcreteVessel, ActorVariable] = dict()
        for vessel in scene.sorted_keys:
            if vessel.is_os:
                vessel_actor_map[vessel] = OSVariable(id=vessel.id)
            else:
                vessel_actor_map[vessel] = TSVariable(id=vessel.id)
        actor_variables : List[ActorVariable] = list(vessel_actor_map.values())
        
        relation_constr_exprs : Set[RelationConstrTerm] = set()
        
        assignments = Assignments(actor_variables)
        assignments.update_from_individual(scene.individual)
        
        vessel_pairs = list(itertools.combinations(scene.keys(), 2))
        for v1, v2 in vessel_pairs:
            var1, var2 = vessel_actor_map[v1], vessel_actor_map[v2]
            head_on_term = RelationConstrClause(RelationConstrTerm({AtVis(var1, var2), HeadOnBear(var1, var2), MayCollide(var1, var2)}))
            overtaking_term = RelationConstrTerm({AtVis(var1, var2), OvertakingBear(var1, var2), MayCollide(var1, var2)})
            crossing_term = RelationConstrTerm({AtVis(var1, var2), CrossingBear(var1, var2), MayCollide(var1, var2)})
            no_collide_out_vis_clause = RelationConstrClause({OutVis(var1, var2), MayCollide(var1, var2, negated=True)})
            if head_on_term.evaluate_penalty(assignments).is_zero:
                relation_constr_exprs.add(head_on_term)
            elif overtaking_term.evaluate_penalty(assignments).is_zero:
                relation_constr_exprs.add(overtaking_term)
            elif crossing_term.evaluate_penalty(assignments).is_zero:
                relation_constr_exprs.add(crossing_term)
            elif no_collide_out_vis_clause.evaluate_penalty(assignments).is_zero:
                relation_constr_exprs.add(no_collide_out_vis_clause)
            else:
                raise Exception('Undefined relation between actors!')
            
        relation_constr_clause = RelationConstrClause([RelationConstrTerm(relation_constr_exprs)])
        
        xl = [var.lower_bounds for var in actor_variables]
        xu = [var.upper_bounds for var in actor_variables]
        return LogicalScenario(RandomInstanceInitializer(actor_variables), relation_constr_clause, xl, xu)   
                
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
        vessels: Dict[VesselClass, ActorVariable] = {vessel_object : ActorVariable(vessel_object) for vessel_object in vessel_objects}
        assignments = Assignments(list(vessels.values()))
        assignments.update_from_individual(scene.individual)
            
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