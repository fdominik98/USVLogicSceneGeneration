
from abc import ABC
from dataclasses import dataclass
from typing import List

from utils.asv_utils import KNOT_TO_MS_CONVERSION, MAX_BEAM, MAX_LENGTH, MAX_SPEED_IN_MS, MIN_BEAM, MIN_LENGTH, MIN_SPEED_IN_MS

"""
Ship types:
tanker, MMSI: 413474690 : 93 x 17 m
tanker, MMSI: 412377520 : 146 x 21 m
tanker, MMSI: 413441230 : 82 x 12 m
tanker, MMSI: 413697340 : 96 x 16 m

container, MMSI: 413146000 : 263 x 32 m
container, MMSI: 412713000 : 294 x 32 m
container, MMSI: 212602000 : 259 x 32 m

cargo vessel, MMSI: 413700110 : 159 x 23 m
cargo vessel, MMSI: 412766340 : 179 x 28 m

High Speed Craft, MMSI: 477937400 : 47 x 12 m
High Speed Craft, MMSI: 477937500 : 47 x 12 m
High Speed Craft, MMSI: 477937200 : 47 x 12 m
High Speed Craft, MMSI: 477525000 : 40 x 15 m
High Speed Craft, MMSI: 477385000 :	45 x 12 m

Passenger ship, MMSI: 477995974 : 25 x 8 m
Passenger ship, MMSI: 477995293 : 30 x 8 m

"""

@dataclass(frozen=True, repr=False)
class VesselType(ABC):
    name : str = 'VesselType'
    min_length : float = MIN_LENGTH
    max_length : float = MAX_LENGTH
    min_speed : float = MIN_SPEED_IN_MS
    max_speed : float = MAX_SPEED_IN_MS
    min_beam : float = MIN_BEAM
    max_beam : float = MAX_BEAM
    
    def do_match(self, length : float, speed : float, beam=None) -> bool:
        return (self.min_length <= length <= self.max_length and
                self.min_speed <= speed <= self.max_speed and
                (beam is None or self.min_beam <= beam <= self.max_beam)
                )
        
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
        
    @staticmethod    
    def get_vessel_type_by_name(name):
        return next((t for t in ALL_VESSEL_TYPES if t.name == name), None)
    
@dataclass(frozen=True, repr=False)
class OtherType(VesselType):
    name : str = 'OtherType'
    pass
    
@dataclass(frozen=True, repr=False)
class CargoShip(VesselType):
    name : str = 'CargoShip'
    min_length = 50
    max_length = 400
    max_speed = 25 * KNOT_TO_MS_CONVERSION
    min_beam = 10
    max_beam = 60
    
@dataclass(frozen=True, repr=False)
class Tanker(VesselType):
    name : str = 'Tanker'
    min_length = 60
    max_length = 350
    max_speed = 20 * KNOT_TO_MS_CONVERSION
    min_beam = 10
    max_beam = 60
    
@dataclass(frozen=True, repr=False)
class ContainerShip(VesselType):
    name : str = 'ContainerShip'
    min_length = 100
    max_length = 400
    max_speed = 25 * KNOT_TO_MS_CONVERSION
    min_beam = 15
    max_beam = 65
    
@dataclass(frozen=True, repr=False)
class PassengerShip(VesselType):
    name : str = 'PassengerShip'
    min_length = 20
    max_length = 350
    max_speed = 40 * KNOT_TO_MS_CONVERSION
    min_beam = 5
    max_beam = 50
    
@dataclass(frozen=True, repr=False)
class FishingShip(VesselType):
    name : str = 'FishingShip'
    min_length = 2
    max_length = 100
    max_speed = 15 * KNOT_TO_MS_CONVERSION
    min_beam = 2
    max_beam = 20
    
ALL_VESSEL_TYPES : List[VesselType] = [OtherType(), Tanker(), CargoShip(), ContainerShip(), PassengerShip(), FishingShip()]