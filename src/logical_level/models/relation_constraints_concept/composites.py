from abc import ABC, abstractmethod
from typing import Set
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_cache import EvaluationCache
from logical_level.models.penalty import Penalty


class RelationConstrComposite(ABC):
    def __init__(self, components : Set['RelationConstrComposite']):
        super().__init__()
        self.components : Set['RelationConstrComposite'] = components
    
    @abstractmethod
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        pass
    
    def evaluate_penalty(self, assignments : Assignments) -> Penalty:
        cache = EvaluationCache(assignments)
        return self._evaluate_penalty(cache)
    
     
class RelationConstrTerm(RelationConstrComposite):
    def __init__(self, components : Set['RelationConstrComposite'] = set()):
        super().__init__(components)
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        return sum([comp._evaluate_penalty(eval_cache) for comp in self.components], Penalty())
    
    def __repr__(self) -> str:
        return f'({" ∧ ".join(f"{comp}" for comp in self.components)})'
    
    
class RelationConstrClause(RelationConstrComposite):
    def __init__(self, components : Set['RelationConstrComposite'] = set()):
        super().__init__(components)
    
    def _evaluate_penalty(self, eval_cache : EvaluationCache) -> Penalty:
        return min([comp._evaluate_penalty(eval_cache) for comp in self.components])
    
    def __repr__(self) -> str:
        return f'({" ∨ ".join(f"{comp}" for comp in self.components)})'