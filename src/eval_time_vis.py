from collections import defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt
from model.data_parser import EvalDataParser
from evolutionary_computation.evaluation_data import EvaluationData

dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()
# Assuming the objects have these attributes: measurement_name, algorithm_desc, config_name, best_fitness
organized_dict : Dict[str, Dict[str, Dict[str, List[EvaluationData]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(List[EvaluationData])))
# Populate the nested dictionary
for eval_data in eval_datas:
    organized_dict[eval_data.measurement_name][eval_data.algorithm_desc][eval_data.config_name].append(eval_data)

# Create the boxplot
plt.boxplot(data, patch_artist=True)

# Add labels and title
plt.xticks(list(range(1, len(dfs) + 1)), df_names)
plt.xlabel('Measurement')
plt.ylabel('Evaluation Time')
plt.title('Boxplot of the evaluation time of the measurements')

# Show the plot
plt.show()

