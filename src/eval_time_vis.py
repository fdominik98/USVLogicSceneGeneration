import matplotlib.pyplot as plt
import pandas as pd
from visualization.data_parser import EvalDataParser

dp = EvalDataParser()

dfs, df_names = dp.load_dirs()

data = [df['evaluation_time'] for df in dfs]

# Create the boxplot
plt.boxplot(data, patch_artist=True)

# Add labels and title
plt.xticks(list(range(1, len(dfs) + 1)), df_names)
plt.xlabel('Measurement')
plt.ylabel('Evaluation Time')
plt.title('Boxplot of the evaluation time of the measurements')

# Show the plot
plt.show()