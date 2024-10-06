from model.environment.usv_environment_desc import F2EnvironmentDesc
from model.relation_types import AnyColregBear, AtVis
from model.environment.functional_models.model_utils import generate_models
from model.environment.functional_models.model_utils import OS, TS1, TS2, TS3, TS4, TS5

six_vessel_interactions = generate_models(F2EnvironmentDesc, [OS, TS1, TS2, TS3, TS4, TS5], lambda: [AtVis(), AnyColregBear()])