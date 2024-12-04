from abc import ABC
import copy
import numpy as np
from asv_utils import EPSILON, KNOT_TO_MS_CONVERSION


class VesselClass(ABC):
    def __init__(self, id : int):
        super().__init__()
        self.id = id
        
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, VesselClass) and
            self.id == value.id)
        
    def __repr__(self) -> str:
        return 'desc'
    
    def __hash__(self):
        return hash((self.id, 'vessel description'))
    
    def is_os(self):
        return isinstance(self, OS)
    

class OS(VesselClass):
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, OS) and super().__eq__(value))
        
    def __repr__(self) -> str:
        return f'OS{self.id}'
    
    def __hash__(self):
        return hash((super().__hash__(), 'OS'))
    
class TS(VesselClass):
    def __eq__(self, value: object) -> bool:
        return (isinstance(value, TS) and super().__eq__(value))
        
    def __repr__(self) -> str:
        return f'TS{self.id}'
    
    def __hash__(self):
        return hash((super().__hash__(), 'TS'))

