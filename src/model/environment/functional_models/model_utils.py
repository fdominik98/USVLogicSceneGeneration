import itertools
from typing import List

from model.environment.usv_environment_desc import USVEnvironmentDesc
from model.vessel import VesselDesc
from model.relation import RelationDesc

OS = VesselDesc(id=0, l=30, b=10, min_speed= 5.0, max_speed=30)
TS1 = VesselDesc(id=1, l=50, b=18, min_speed= 5.0, max_speed=25)
TS2 = VesselDesc(id=2, l=20, b=10, min_speed= 5.0, max_speed=30)
TS3 = VesselDesc(id=3, l=20, b=10, min_speed= 5.0, max_speed=30)
TS4 = VesselDesc(id=4, l=20, b=10, min_speed= 5.0, max_speed=30)
TS5 = VesselDesc(id=5, l=20, b=10, min_speed= 5.0, max_speed=30)

def generate_models(config_class : USVEnvironmentDesc.__class__, objects : List[VesselDesc], relation_type) -> List[USVEnvironmentDesc]:
    truth_table = itertools.product([0, 1], repeat=len(objects) - 1)
    # Generate pairs based on the truth table
    pairs = [
        [[objects[0], objects[i + 1]] if comb[i] else [objects[i + 1], objects[0]] for i in range(len(objects) - 1)]
        for comb in truth_table
    ]

    interactions : List[config_class] = [ ]

    for i, pair in enumerate(pairs):
        interactions.append(config_class(f'{len(objects)}_vessel_{i+1}_{config_class.group}', objects,
                            [RelationDesc(p[0], relation_type(), p[1]) for p in pair]),       
        )
    return interactions