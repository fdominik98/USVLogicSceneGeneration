from visualization.data_parser import DataParser
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.plotting import parallel_coordinates
from mpl_toolkits.mplot3d import Axes3D


dp = DataParser()
df = dp.dfs[0]
df_sorted = df.sort_values(by=['result', 'evaluation_time'], ascending=[False, True])
df_sorted = df_sorted.drop(columns=['num_parents_mating', 'best_solution', 'config_name'])
#df_sorted = df_sorted.drop(columns=['actual_number_of_generations'])

df_simple_sorted = df_sorted.drop(columns=['evaluation_time'])
df_best = df_sorted.head(50)
df_simple_best = df_simple_sorted.head(1000)

# Display the DataFrame as a table
fig, ax = plt.subplots(figsize=(15, 10))
ax.axis('tight')
ax.axis('off')
table = ax.table(cellText=df_best.values, colLabels=df_best.columns, cellLoc='center', loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.auto_set_column_width(col=list(range(len(df_best.columns))))
ax.set_title(f'All samples: {len(df_sorted)}', fontsize=15, pad=40)

# Columns you want to color
columns_to_white = ['result', 'evaluation_time', 'actual_number_of_generations']
# Get the index of the columns to color
columns_to_white_indices = [df_best.columns.get_loc(col) for col in columns_to_white]

# Iterate over the table to set the background color
for key, cell in table.get_celld().items():
    row, col = key
    if col in columns_to_white_indices:
        cell.set_facecolor('white')
    else:
        cell.set_facecolor('lightgreen')

plt.show()


# Correlation Heatmap
correlation_matrix = df_sorted.corr()

plt.figure(figsize=(15, 10))
heatmap = sns.heatmap(
    correlation_matrix, 
    annot=True, 
    cmap='coolwarm', 
    vmin=-1, 
    vmax=1,
    annot_kws={"size": 10},  # Font size for annotations
    linewidths=0.5,  # Line width between cells
    linecolor='white'  # Line color between cells
)

# Customize the heatmap's appearance
heatmap.set_title('Correlation Heatmap', fontsize=10)
heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=25, horizontalalignment='right', fontsize=12)
heatmap.set_yticklabels(heatmap.get_yticklabels(), rotation=0, fontsize=12)

plt.show()


# 3D Scatter Plot
# fig = plt.figure(figsize=(15, 10))
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(df_simple_best['population_size'], df_simple_best['number_of_generations'],
#            df_simple_best['result'], c=df_simple_best['result'], cmap='viridis')
# ax.set_xlabel('population_size')
# ax.set_ylabel('number_of_generations')
# ax.set_zlabel('Result')
# plt.show()

# Pairplot
sns.pairplot(df_simple_best, hue='result', diag_kind='kde', palette='coolwarm', markers='+')
plt.show()

