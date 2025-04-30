from typing import Set
from logical_level.models.actor_variable import ActorVariable, StaticObstacleVariable, VesselVariable
from logical_level.models.relation_constraints_concept.composites import RelationConstrClause, RelationConstrComposite, RelationConstrTerm
from logical_level.models.relation_constraints_concept.literals import InBowSectorOf, InPortSideSectorOf, AtVis, MayCollide, SoonMeet, InStarboardSideSectorOf, InSternSectorOf, OutVis

class BinaryPredicate(RelationConstrTerm):
    def __init__(self, name : str,  var1 : ActorVariable, var2 : ActorVariable, components : Set[RelationConstrComposite]):
        super().__init__(components)
        self.name = name
        self.var1 : ActorVariable = var1
        self.var2 : VesselVariable = var2
        
    def __repr__(self) -> str:
        return f'{self.name}({self.var1}, {self.var2})'
    
    
class AtVisAndMayCollideSoon(BinaryPredicate):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable):
        super().__init__('AtVisAndMayCollideSoon', var1, var2,
                         {MayCollide(var1, var2), SoonMeet(var1, var2), AtVis(var1, var2)}) 
class AtVisAndMayCollide(BinaryPredicate):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable):
        super().__init__('AtVisAndMayCollide', var1, var2,
                         {MayCollide(var1, var2), AtVis(var1, var2)})
        
class OutVisOrMayNotCollide(BinaryPredicate):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable):
        super().__init__('OutVisOrMayNotCollide', var1, var2,
                         {RelationConstrClause({MayCollide(var1, var2, negated=True), OutVis(var1, var2)}),})
        
class InMastheadSectorOf(BinaryPredicate):
    def __init__(self, var1 : ActorVariable, var2 : VesselVariable):
        super().__init__('InMastheadSectorOf', var1, var2,
                         {RelationConstrClause({InPortSideSectorOf(var1, var2), InStarboardSideSectorOf(var1, var2)}),})

class HeadOn(BinaryPredicate):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable):
        super().__init__('HeadOn', var1, var2,
                         {InBowSectorOf(var1, var2), InBowSectorOf(var2, var1), AtVisAndMayCollideSoon(var1, var2)})
    

class CrossingFromPort(BinaryPredicate):
    def __init__(self,  var1 : VesselVariable, var2 : VesselVariable):
        not_in_mutual_head_on_sector = RelationConstrTerm({InBowSectorOf(var1, var2, negated=True),
                                            InBowSectorOf(var2, var1, negated=True)})
        super().__init__('CrossingFromPort', var1, var2,
                         {InPortSideSectorOf(var1, var2), InStarboardSideSectorOf(var2, var1),
                          AtVisAndMayCollideSoon(var1, var2), not_in_mutual_head_on_sector})
               
class OvertakingToPort(BinaryPredicate):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable):
        super().__init__('OvertakingToPort', var1, var2,
                         {InSternSectorOf(var1, var2), InPortSideSectorOf(var2, var1), AtVisAndMayCollideSoon(var1, var2)})
        
class OvertakingToStarboard(BinaryPredicate):
    def __init__(self, var1 : VesselVariable, var2 : VesselVariable):
        super().__init__('OvertakingToStarboard', var1, var2,
                         {InSternSectorOf(var1, var2), InStarboardSideSectorOf(var2, var1), AtVisAndMayCollideSoon(var1, var2)})
        
        
class DangerousHeadOnSectorOf(BinaryPredicate):
    def __init__(self, var1 : StaticObstacleVariable, var2 : VesselVariable):
        super().__init__('DangerousHeadOnSectorOf', var1, var2,
                         {InBowSectorOf(var1, var2), AtVisAndMayCollide(var1, var2)})
    