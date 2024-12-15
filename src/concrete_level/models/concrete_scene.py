from dataclasses import dataclass, field
from typing import Dict, List, Optional
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.vessel_state import VesselState

@dataclass(frozen=True)
class ConcreteScene():   
    
    _data : Dict[ConcreteVessel, VesselState]
    dcpa : Optional[float] = None
    tcpa : Optional[float] = None
    danger_sector : Optional[float] = None
    proximity_index : Optional[float] = None
    
    def __post_init__(self):
        object.__setattr__(self, '_data', dict(self._data))
            
    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

    def values(self):
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
    
    @property
    def individual(self) -> List[float]:        
        individual : List[float] = []
        for vessel, state in self.sorted_items:
            individual += [state.x, state.y, state.heading, vessel.length, state.speed]
        return individual
    
    @property
    def vessel_num(self) -> int:
        return len(self)
    