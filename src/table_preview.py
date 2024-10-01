from visualization.colreg_scenarios.colreg_plot_manager import ColregPlotManager
from model.data_parser import EvalDataParser
import matplotlib.pyplot as plt
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST
from model.environment.usv_environment import USVEnvironment

while(True):
    dp = EvalDataParser()
    dfs, df_names = dp.load_dirs()

    if len(dfs) == 0:
        exit()

    for i, df in enumerate(dfs):
        page_size = 45
        current_page = 0
        table = None
        
        df_sorted = df.sort_values(by=['best_fitness_index', 'evaluation_time'], ascending=[True, True])
        
        df_best = df_sorted.drop(columns=['num_parents_mating', 'best_solution', 'measurement_name', 'path'])
        #df_best = df_best.drop(columns=['actual_number_of_generations'])

        # Display the DataFrame as a table
        fig, ax = plt.subplots(figsize=(15, 10))
        fig : plt.Figure = fig
        ax : plt.Axes = ax 
        ax.axis('tight')
        ax.axis('off')
        
        # Columns you want to color
        columns_to_white = ['best_fitness_index', 'evaluation_time', 'number_of_generations']
        # Get the index of the columns to color
        columns_to_white_indices = [df_best.columns.get_loc(col) for col in columns_to_white]
        
        def update_table(page):
            ax.clear()  # Clear the previous table
            ax.axis('off')  # Hide the axes
            
            start_idx = page * page_size
            end_idx = start_idx + page_size
            df_best_chunk = df_best.iloc[start_idx:end_idx]
            table_data = df_best_chunk.values
            
            ax.set_title(f'Samples: {start_idx + 1} - {end_idx} / {len(df_best)}', fontsize=13, pad=40)
            # Create the updated table
            table = ax.table(cellText=table_data, colLabels=df_best_chunk.columns, rowLabels=df_best_chunk.index + 1, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.auto_set_column_width(col=list(range(len(df_best_chunk.columns))))
            table.set_fontsize(10)
            fig.canvas.draw_idle()
            return table
            
        def reset_background():
            global table
            # Iterate over the table to set the background color
            for key, cell in table.get_celld().items():
                row, col = key
                if col in columns_to_white_indices:
                    cell.set_facecolor('white')
                else:
                    cell.set_facecolor('lightgreen')
                cell.set_text_props(color='black')
        table = update_table(current_page)
        reset_background()
                
                
        def get_row_y(row):
            global table
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
            global table
            row_number = -1            
            for row in range(1, len(df) + 1):
                first_y = get_row_y(row - 1)
                second_y = get_row_y(row)
                
                if event.ydata <= first_y and event.ydata > second_y:
                    row_number = row -1
                    break
                print(row_number)
                data = df_sorted.iloc[row_number]
                print(data)
            if event.button == 1:                
                if row_number >= 0 and row_number < len(df):
                    config = USV_ENV_DESC_LIST[data['config_name']]
                    env = USVEnvironment(config).update(data['best_solution'])
                    ColregPlotManager(env)
            if event.button == 3:                
                selected = table[(row_number, 0)].get_facecolor() == 'black' 
                reset_background()   
                if selected:
                    return               
                for j in range(len(df_best.columns)):
                    table[(row_number+1, j)].set_facecolor('black')
                    table[(row_number+1, j)].set_text_props(color='white')
                fig.canvas.draw_idle()
                
        def on_key(event):
            global current_page
            global table
            if event.key == 'right':  # Right arrow key for next page
                if (current_page + 1) * page_size < len(df):
                    current_page += 1
                    table = update_table(current_page)
                    reset_background()
            elif event.key == 'left':  # Left arrow key for previous page
                if current_page > 0:
                    current_page -= 1
                    table = update_table(current_page)
                    reset_background()
                
                
        # Connect the click event to the function
        fig.canvas.mpl_connect('button_press_event', on_click)
        fig.canvas.mpl_connect('key_press_event', on_key)
        fig.suptitle(df_names[i])
        plt.show()