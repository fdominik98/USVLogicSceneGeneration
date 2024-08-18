import random
from model.usv_config import MAX_COORD, MIN_COORD, MAX_DISTANCE
from model.vessel import Vessel, VesselDesc
from model.colreg_situation import ColregSituation
from model.colreg_situation_desc import ColregSituationDesc

class RandomInstanceInitializer():
    def __init__(self, vessel_descs : list[VesselDesc], colreg_situation_descs : list[ColregSituationDesc]) -> None:
        self.vessel_descs = vessel_descs
        self.actor_num = len(vessel_descs)
        self.colreg_situation_descs = colreg_situation_descs
        self.max_distance = MAX_DISTANCE(self.actor_num)
        self.max_coord = MAX_COORD(self.actor_num)
        
    def get_population(self, pop_size) -> list[list[float]]:
        result : list[list[float]] = []
        for i in range(int(pop_size)):
            population : list[float] = []
            for vessel_desc in self.vessel_descs:
                group = [random.uniform(MIN_COORD, self.max_coord),
                         random.uniform(MIN_COORD, self.max_coord),
                         random.uniform(-vessel_desc.max_speed, vessel_desc.max_speed),
                         random.uniform(-vessel_desc.max_speed, vessel_desc.max_speed)]
                population.extend(group)
            result.append(population)
        return result
    
    
    def convert_population_to_objects(self, states: list[float]) -> tuple[list[Vessel], set[ColregSituation]]:
        vessels: list[Vessel] = []
        for i, vessel_desc in enumerate(self.vessel_descs):
            vessel = Vessel(vessel_desc)
            vessel.update(states[i * 4], states[i * 4 + 1], states[i * 4 + 2], states[i * 4 + 3])
            vessels.append(vessel)
            
        colreg_situations : set[ColregSituation] = set()        
        for colreg_situation_desc in self.colreg_situation_descs:
            vd1 = colreg_situation_desc.vd1
            vd2 = colreg_situation_desc.vd2
            colreg_class = colreg_situation_desc.colreg_class
            colreg_situations.add(colreg_class(vessels[vd1.id], vessels[vd2.id], colreg_situation_desc.distance, self.max_distance))
        return vessels, colreg_situations
    
    
    def get_one_population_as_objects(self) -> tuple[list[Vessel], set[ColregSituation]]:
        return self.convert_population_to_objects(self.get_population(1)[0])