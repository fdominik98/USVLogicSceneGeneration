import random
from model.usv_config import MAX_COORD, MAX_HEADING, MIN_COORD, MIN_HEADING, OWN_VESSEL_STATES, VARIABLE_NUM
from model.vessel import Vessel, VesselDesc
from model.colreg_situation import ColregSituation
from model.colreg_situation_desc import ColregSituationDesc
from abc import ABC, abstractmethod

class InstanceInitializer(ABC):    
    def __init__(self, vessel_descs : list[VesselDesc], colreg_situation_descs : list[ColregSituationDesc]) -> None:
        self.vessel_descs = vessel_descs
        self.actor_num = len(vessel_descs)
        self.colreg_situation_descs = colreg_situation_descs
       
    @abstractmethod     
    def get_population(self, pop_size) -> list[list[float]]:
        pass

    def convert_population_to_objects(self, states: list[float]) -> tuple[list[Vessel], set[ColregSituation]]:
        states = OWN_VESSEL_STATES + states
        vessels: list[Vessel] = []
        for vessel_desc in self.vessel_descs:
            vessel = Vessel(vessel_desc)
            vessel.update(states[vessel.id * VARIABLE_NUM],
                            states[vessel.id * VARIABLE_NUM + 1],
                            states[vessel.id * VARIABLE_NUM + 2],
                            states[vessel.id * VARIABLE_NUM + 3])
            vessels.append(vessel)
            
        colreg_situations : set[ColregSituation] = set()        
        for colreg_situation_desc in self.colreg_situation_descs:
            vd1 = colreg_situation_desc.vd1
            vd2 = colreg_situation_desc.vd2
            colreg_class = colreg_situation_desc.colreg_class
            colreg_situations.add(colreg_class(vessels[vd1.id], vessels[vd2.id]))
        return vessels, colreg_situations
    
    
    def get_one_population_as_objects(self) -> tuple[list[Vessel], set[ColregSituation]]:
        return self.convert_population_to_objects(self.get_population(1)[0])
    
class RandomInstanceInitializer(InstanceInitializer):
    def __init__(self, vessel_descs : list[VesselDesc], colreg_situation_descs : list[ColregSituationDesc]) -> None:
        super().__init__(vessel_descs, colreg_situation_descs)
        
    def get_population(self, pop_size) -> list[list[float]]:
        result : list[list[float]] = []
        for i in range(int(pop_size)):
            population : list[float] = [random.uniform(self.vessel_descs[0].min_speed, self.vessel_descs[0].max_speed)]
            for vessel_desc in self.vessel_descs[1:]:
                group = [random.uniform(MIN_COORD, MAX_COORD),
                        random.uniform(MIN_COORD, MAX_COORD),
                        random.uniform(MIN_HEADING, MAX_HEADING),
                        random.uniform(vessel_desc.min_speed, vessel_desc.max_speed)]
                population.extend(group)
            result.append(population)
        return result  
    
class DeterministicInitializer(InstanceInitializer):
    def __init__(self, vessel_descs : list[VesselDesc], colreg_situation_descs : list[ColregSituationDesc]) -> None:
        super().__init__(vessel_descs, colreg_situation_descs)
        
    def get_population(self, pop_size) -> list[list[float]]:
        result : list[list[float]] = []
        for i in range(int(pop_size)):
            population : list[float] = [(self.vessel_descs[0].min_speed + self.vessel_descs[0].max_speed) / 2.0]
            for vessel_desc in self.vessel_descs[1:]:
                group = [MAX_COORD / 2, MAX_COORD / 2, 0, (vessel_desc.min_speed + vessel_desc.max_speed) / 2]
                population.extend(group)
            result.append(population)
        return result  
    
    