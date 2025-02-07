from dataclasses import dataclass
from itertools import combinations
from typing import Any, Dict, List, Optional, Set, Type
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.vessel_state import VesselState
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.models.actor_variable import ActorVariable
from logical_level.models.relation_constraints import DoCollide, MayCollide
from utils.serializable import Serializable

@dataclass(frozen=True)
class ConcreteScene(Serializable):       
    _data : Dict[ConcreteVessel, VesselState]
    dcpa : Optional[float] = None
    tcpa : Optional[float] = None
    danger_sector : Optional[float] = None
    proximity_index : Optional[float] = None
    
    @property
    def has_risk_metrics(self):
        return all(value is not None for value in [self.dcpa, self.tcpa, self.danger_sector, self.proximity_index])
    
    def __post_init__(self):
        object.__setattr__(self, '_data', dict(self._data))
            
    def __getitem__(self, key):
        return self._data[key]

    @property
    def actors(self):
        return [actor for actor, _ in self.sorted_items]
    
    @property
    def all_actor_pairs(self):
        return {(ai, aj) for ai, aj in combinations(self.actors, 2)}

    @property
    def actor_states(self):
        return self._data.values()

    def items(self):
        return self._data.items()
    
    @property
    def sorted_items(self):
        return sorted(self.items(), key=lambda item: item[0].id)
    
    @property
    def sorted_keys(self) -> List[ConcreteVessel]:
        return [key for key, value in self.sorted_items]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"
    
    def as_dict(self) -> Dict[ConcreteVessel, VesselState]:
        return self._data
    
    @property
    def individual(self) -> List[float]:        
        individual : List[float] = []
        for vessel, state in self.sorted_items:
            individual += [state.x, state.y, state.heading, vessel.length, state.speed]
        return individual
    
    @property
    def vessel_number(self) -> int:
        return len(self)
    
    @property
    def os(self) -> ConcreteVessel:
        vessel = next((actor for actor in self.actors if actor.is_os), None)
        if vessel is None:
            raise ValueError('No OS in the scene.')
        return vessel
    
    @property
    def non_os(self) -> Set[ConcreteVessel]:
        return {actor for actor in self.actors if not actor.is_os}
    
    def assignments(self, variables : List[ActorVariable]) -> Assignments:
        if len(self) != len(variables):
            raise ValueError('Variable and actor numbers do not match.')
        for actor, var in zip(self.sorted_keys, variables):
            if actor.id != var.id:
                raise ValueError('Insufficient order of actors and variables.')
        return Assignments(variables).update_from_individual(self.individual)
    
    def may_collide(self, actor1 : ConcreteVessel, actor2 : ConcreteVessel) -> bool:
        vars = {v : v.logical_variable for v in self.actors}
        return MayCollide(vars[actor1], vars[actor2]).evaluate_penalty(self.assignments(list(vars.values()))).is_zero
    
    def do_collide(self, actor1 : ConcreteVessel, actor2 : ConcreteVessel) -> bool:
        vars = {v : v.logical_variable for v in self.actors}
        return DoCollide(vars[actor1], vars[actor2]).evaluate_penalty(self.assignments(list(vars.values()))).is_zero
    
    def others_than(self, vessel : ConcreteVessel) -> List[ConcreteVessel]:
        return [v for v in self.actors if v is not vessel]
    
    
    def to_dict(self):
        result = {}
        for key, value in self.__dict__.items():
            if key == '_data':
                result[key] = [(vessel.to_dict(), state.to_dict())
                    for vessel, state in self._data.items()]
            else:  # Handle primitive types
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls: Type['ConcreteScene'], data: Dict[str, Any]) -> 'ConcreteScene':
        copy_data = data.copy()
        for attr, value in data.items():
            if attr == '_data':
                copy_data[attr] = {
                        ConcreteVessel.from_dict(vessel):
                        VesselState.from_dict(state)
                        for vessel, state in value
                    }
        return ConcreteScene(**copy_data)
    
    @staticmethod
    def is_os_ts_pair(v1 : ConcreteVessel, v2 : ConcreteVessel) -> bool:
        return (v1.is_os and not v2.is_os) or (v2.is_os and not v1.is_os)
    