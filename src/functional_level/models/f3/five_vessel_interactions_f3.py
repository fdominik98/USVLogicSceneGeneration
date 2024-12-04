from logical_level.models.relation_types import any_colreg_init
from functional_level.metamodels.functional_scenario import F3EnvironmentDesc
from functional_level.models.model_utils import generate_models
from functional_level.models.model_utils import TS1, TS2, TS3, TS4

five_vessel_interactions = generate_models(F3EnvironmentDesc, [TS1, TS2, TS3, TS4], any_colreg_init)