from functional_level.metamodels.functional_scenario import F2EnvironmentDesc
from logical_level.models.relation_types import AnyColregBear, AtVis
from functional_level.models.model_utils import generate_models
from functional_level.models.model_utils import TS1, TS2

three_vessel_interactions = generate_models(F2EnvironmentDesc, [TS1, TS2], lambda: [AtVis(), AnyColregBear()])
