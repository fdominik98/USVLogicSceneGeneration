from visualization.colreg_plot import ColregPlot
from visualization.data_parser import DataParser
import matplotlib.pyplot as plt
from model.colreg_situation_configs import usv_environment_configs
from model.usv_environment import USVEnvironment

dp = DataParser()

for df in dp.dfs:

    df_sorted = df.sort_values(by=['result', 'evaluation_time'], ascending=[False, True])
    
    df_best = df_sorted.drop(columns=['num_parents_mating', 'best_solution', 'config_name'])
    #df_best = df_best.drop(columns=['actual_number_of_generations'])
    df_best = df_best.head(45)

    # Display the DataFrame as a table
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df_best.values, colLabels=df_best.columns, rowLabels=df_best.index + 1, cellLoc='center', loc='center')
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
            
    def get_row_y(row):
         # Get the cell of the first row (excluding header)
        row_cell = table[(row, 0)]  # (row, column) index, (0, 0) would be the header cell if present
        # Get the bounding box of the cell
        bbox = row_cell.get_window_extent(fig.canvas.get_renderer())

        # Convert bbox to data coordinates
        inv = ax.transData.inverted()
        data_bbox = inv.transform(bbox)

        # The y-coordinate of the first row
        return data_bbox[0][1]
            

    def on_click(event):
        row_number = -1            
        for row in range(1, len(df) + 1):
            first_y = get_row_y(row - 1)
            second_y = get_row_y(row)
            
            if event.ydata <= first_y and event.ydata > second_y:
                row_number = row -1
                break
        
        if row_number >= 0 and row_number < len(df):
            print(row_number)
            data = df_sorted.iloc[row_number]
            print(data)
            config = usv_environment_configs[data['config_name']]
            env = USVEnvironment(config).update(data['best_solution'])
            ColregPlot(env)
                
    # Connect the click event to the function
    fig.canvas.mpl_connect('button_press_event', on_click)
    

    
    plt.show()