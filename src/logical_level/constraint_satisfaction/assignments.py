from typing import Dict, List, Union

import numpy as np
from logical_level.models.values import Values
from logical_level.models.actor_variable import ActorVariable

class Assignments(Dict[ActorVariable, Values]):
    def __init__(self, actor_variables : List[ActorVariable] = [], *args, **kwargs):
        super().__init__({var : None for var in actor_variables}, *args, **kwargs)

    def update_from_individual(self, states : Union[np.ndarray, List[float]]) -> 'Assignments':
        if len(states) != sum(len(var) for var in self.keys()):
            raise Exception("the variable number is insufficient.")
        
        for i, var in enumerate(self.keys()):
            var_len = len(var)
            self[var] = Values(x=states[i * var_len],
                                y=states[i * var_len + 1],
                                h=states[i * var_len + 2],
                                l=states[i * var_len + 3],
                                sp=states[i * var_len + 4])   
        return self
            
        
