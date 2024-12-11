from logical_level.models.constraint_types import AnyColregBear, AtVis
from functional_level.metamodels.functional_scenario import F2EnvironmentDesc
from functional_level.models.model_utils import generate_models
from functional_level.models.model_utils import TS1, TS2, TS3, TS4

five_vessel_interactions = generate_models(F2EnvironmentDesc, [TS1, TS2, TS3, TS4], lambda: [AtVis(), AnyColregBear()])