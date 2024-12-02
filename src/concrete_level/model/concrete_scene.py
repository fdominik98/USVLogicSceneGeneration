from dataclasses import dataclass, field
from typing import Dict, Optional
from concrete_level.model.concrete_vessel import ConcreteVessel
from concrete_level.model.vessel_state import VesselState

@dataclass(frozen=True)
class ConcreteScene():   
    
    _data : Dict[ConcreteVessel, VesselState]
    dcpa : Optional[float] = None
    tcpa : Optional[float] = None
    danger_sector : Optional[float] = None
    proximity_index : Optional[float] = None
    
    vessel_number : int = field(init=False)
    
    def __post_init__(self):
        object.__setattr__(self, 'vessel_number', len(self))
        object.__setattr__(self, '_data', dict(self._data))
            
    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})" 
    