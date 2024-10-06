from model.environment.usv_environment_desc import F2EnvironmentDesc
from model.relation_types import AnyColregBear, AtVis
from model.environment.functional_models.model_utils import generate_models
from model.environment.functional_models.model_utils import TS1, TS2

three_vessel_interactions = generate_models(F2EnvironmentDesc, [TS1, TS2], lambda: [AtVis(), AnyColregBear()])
