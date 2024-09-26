import matplotlib.pyplot as plt
import pandas as pd
from model.data_parser import EvalDataParser
from collections import defaultdict
from IPython.display import display
from pprint import pprint

dp = EvalDataParser()
df = dp.load_dirs_merged()
# Assuming the objects have these attributes: measurement_name, algorithm_desc, config_name, best_fitness
organized_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
# Populate the nested dictionary
for index, row in df.iterrows():
    organized_dict[row['measurement_name']][row['algorithm_desc']][row['config_name']].append(row)

# Sort each list by best_fitness in ascending order
for measurement_name, alg_dict in organized_dict.items():
    for algorithm_desc, config_dict in alg_dict.items():
        for config_name, obj_list in config_dict.items():
            config_dict[config_name] = sorted(obj_list, key=lambda o: o['result'])[0]

pprint(organized_dict)

# dfs, df_names = dp.load_dirs()
# data = [df['evaluation_time'] for df in dfs]
# # Create the boxplot
# plt.boxplot(data, patch_artist=True)

# # Add labels and title
# plt.xticks(list(range(1, len(dfs) + 1)), df_names)
# plt.xlabel('Measurement')
# plt.ylabel('Evaluation Time')
# plt.title('Boxplot of the evaluation time of the measurements')

# # Show the plot
# plt.show()

