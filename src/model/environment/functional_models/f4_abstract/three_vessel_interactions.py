from model.environment.functional_models.model_utils import TS1, TS2, generate_abstract_models

three_vessel_interactions = four_vessel_interactions = generate_abstract_models([TS1, TS2])
