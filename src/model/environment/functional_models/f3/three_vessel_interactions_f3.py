from model.environment.usv_environment_desc import F3EnvironmentDesc
from model.relation_types import any_colreg_init
from model.environment.functional_models.model_utils import generate_models
from model.environment.functional_models.model_utils import TS1, TS2

three_vessel_interactions = generate_models(F3EnvironmentDesc, [TS1, TS2], any_colreg_init)