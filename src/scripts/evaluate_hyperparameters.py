from collections import Counter
from concrete_level.data_parser import EvalDataParser
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData

dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()

# Step 1: Create a key based on config attributes
def get_config_key(obj : EvaluationData) -> tuple:
    
    return (
        obj.population_size,
        obj.mutate_eta,
        obj.mutate_prob,
        obj.crossover_eta,
        obj.crossover_prob
    )

# Step 2: Count all configurations
config_counter = Counter(get_config_key(obj) for obj in eval_datas if obj.is_valid)

# Step 3: Find the most common config
most_common_config, count = config_counter.most_common(1)[0]

# Step 4: Get all objects with this config
grouped_objects = [obj for obj in eval_datas if get_config_key(obj) == most_common_config and obj.is_valid]

# Print results
print(f"Most common configuration (appears {count} times): {most_common_config}")
print("Objects with this configuration:")
for obj in grouped_objects:
    print(vars(obj))