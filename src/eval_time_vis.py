import matplotlib.pyplot as plt
import pandas as pd
from visualization.data_parser import DataParser

dp = DataParser()

data = [df['evaluation_time'] for df in dp.dfs]

# Create the boxplot
plt.boxplot(data, patch_artist=True)

# Add labels and title
plt.xticks(list(range(1, len(dp.dfs) + 1)), dp.df_names)
plt.xlabel('Measurement')
plt.ylabel('Evaluation Time')
plt.title('Boxplot of the evaluation time of the measurements')

# Show the plot
plt.show()