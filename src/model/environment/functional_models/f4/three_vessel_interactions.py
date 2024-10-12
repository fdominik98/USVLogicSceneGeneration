from model.environment.functional_models.model_utils import TS1, TS10, TS2, TS3, TS4, TS5, TS6, TS7, TS8, TS9, generate_abstract_models

three_vessel_interactions = generate_abstract_models([TS1, TS2])

# print(len(generate_abstract_models([TS1, TS2])))
# print(len(generate_abstract_models([TS1, TS2, TS3])))
# print(len(generate_abstract_models([TS1, TS2, TS3, TS4])))
# print(len(generate_abstract_models([TS1, TS2, TS3, TS4, TS5])))
# print(len(generate_abstract_models([TS1, TS2, TS3, TS4, TS5, TS6])))
# print(len(generate_abstract_models([TS1, TS2, TS3, TS4, TS5, TS6, TS7])))
# print(len(generate_abstract_models([TS1, TS2, TS3, TS4, TS5, TS6, TS7, TS8])))
# print(len(generate_abstract_models([TS1, TS2, TS3, TS4, TS5, TS6, TS7, TS8, TS9])))
# print(len(generate_abstract_models([TS1, TS2, TS3, TS4, TS5, TS6, TS7, TS8, TS9, TS10])))