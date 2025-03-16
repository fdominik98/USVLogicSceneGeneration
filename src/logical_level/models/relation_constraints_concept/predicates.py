from typing import Set
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache
from logical_level.models.actor_variable import ActorVariable, VesselVariable
from logical_level.models.relation_constraints_concept.composites import RelationConstrClause, RelationConstrComposite, RelationConstrTerm
from logical_level.models.relation_constraints_concept.literals import InHeadOnSectorOf, InPortSideSectorOf, AtVis, MayCollide, InStarboardSideSectorOf, InSternSectorOf, OutVis

class BinaryPredicate(RelationConstrTerm):
    def __init__(self, name : str,  var1 : ActorVariable, var2 : ActorVariable, components : Set[RelationConstrComposite]):
        super().__init__(components)
        self.name = name
        self.var1 : ActorVariable = var1
        self.var2 : VesselVariable = var2
        
    def __repr__(self) -> str:
        return f'{self.name}({self.var1}, {self.var2})'
    
class AtVisAndMayCollide(BinaryPredicate):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable):
        super().__init__('AtVisAndMayCollide', var1, var2,
                         {MayCollide(var1, var2), AtVis(var1, var2)})
        
class OutVisOrMayNotCollide(BinaryPredicate):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable):
        super().__init__('OutVisOrMayNotCollide', var1, var2,
                         {RelationConstrClause({MayCollide(var1, var2, negated=False), OutVis(var1, var2)}),})
        
class InMastheadSectorOf(BinaryPredicate):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable):
        super().__init__('InMastheadSectorOf', var1, var2,
                         {RelationConstrClause({InPortSideSectorOf(var1, var2), InStarboardSideSectorOf(var1, var2)}),})

class HeadOn(BinaryPredicate):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable):
        super().__init__('HeadOn', var1, var2,
                         {InHeadOnSectorOf(var1, var2), InHeadOnSectorOf(var2, var1), AtVisAndMayCollide(var1, var2)})
    

class CrossingFromPort(BinaryPredicate):
    def __init__(self,  var1 : VesselVariable, var2 : VesselVariable):
        not_in_mutual_head_on_sector = RelationConstrClause({InHeadOnSectorOf(var1, var2, negated=True),
                                            InHeadOnSectorOf(var2, var1, negated=True)})
        super().__init__('CrossingFromPort', var1, var2,
                         {InPortSideSectorOf(var1, var2), InStarboardSideSectorOf(var2, var1),
                          AtVisAndMayCollide(var1, var2), not_in_mutual_head_on_sector})
               
class OvertakingToPort(BinaryPredicate):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable):
        super().__init__('OvertakingToPort', var1, var2,
                         {InSternSectorOf(var1, var2), InPortSideSectorOf(var2, var1), AtVisAndMayCollide(var1, var2)})
        
class OvertakingToStarboard(BinaryPredicate):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable):
        super().__init__('OvertakingToStarboard', var1, var2,
                         {InSternSectorOf(var1, var2), InStarboardSideSectorOf(var2, var1), AtVisAndMayCollide(var1, var2)})
        
class HeadOnSoft(BinaryPredicate):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable):
        super().__init__('HeadOnSoft', var1, var2,
                         {InHeadOnSectorOf(var1, var2), InHeadOnSectorOf(var2, var1), MayCollide(var1, var2)})
    

class CrossingFromPortSoft(BinaryPredicate):
    def __init__(self,  var1 : VesselVariable, var2 : VesselVariable):
        not_in_mutual_head_on_sector = RelationConstrClause({InHeadOnSectorOf(var1, var2, negated=True),
                                            InHeadOnSectorOf(var2, var1, negated=True)})
        super().__init__('CrossingFromPortSoft', var1, var2,
                         {InPortSideSectorOf(var1, var2), InStarboardSideSectorOf(var2, var1),
                          MayCollide(var1, var2), not_in_mutual_head_on_sector})
               
class OvertakingSoft(BinaryPredicate):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable):
        super().__init__('OvertakingSoft', var1, var2,
                         {InSternSectorOf(var1, var2), InMastheadSectorOf(var2, var1), MayCollide(var1, var2)})
    