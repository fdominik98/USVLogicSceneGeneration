
import pprint
import queue
import threading
from model.data_parser import EvalDataParser
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST
from model.environment.usv_environment import USVEnvironment
import dash
from dash import dash_table, html
from dash.dependencies import Input, Output


class DashThread(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True, name='Dash Thread')
        self.data_queue : queue.Queue[USVEnvironment] = queue.Queue()
        dp = EvalDataParser()
        df = dp.load_dirs_merged()
        hidden_columns = ['best_solution', 'path', 'risk_vector', 'error_message', 'best_fitness']

        self.app = dash.Dash(__name__)

        self.app.layout = html.Div([
            dash_table.DataTable(
                id='table',
                data=df.drop(columns=hidden_columns).to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns if i not in hidden_columns],
                page_size=30,  # pagination
                sort_action='native',  # sorting
                filter_action='native',  # filtering
                row_selectable='single',  # Allow selecting a single row
                selected_rows=[],
                
                # Prettify Table
                style_table={'height': '1000px', 'overflowY': 'auto', 'width': '100%', 'margin': '10px 10px 10px 10px'},
                style_cell={
                    'textAlign': 'center',
                    'padding': '8px',
                    'font_family': 'Arial, sans-serif',
                    'font_size': '14px',
                    'backgroundColor': '#f9f9f9',  # light gray background
                    'border': '1px solid #ddd'  # light border
                },
                style_header={
                    'backgroundColor': '#4CAF50',  # green header
                    'fontWeight': 'bold',
                    'color': 'white',
                    'border': '1px solid black'  # bold header border
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f2f2f2'  # Alternate row color (light gray)
                    },
                    {
                        'if': {'row_index': 'even'},
                        'backgroundColor': '#ffffff'  # White background for even rows
                    },
                    {
                        'if': {
                            'column_id': 'A',  # Highlight column 'A'
                        },
                        'backgroundColor': '#e0f7fa',
                        'color': '#00796b',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'state': 'selected'  # Styling for the selected row
                        },
                        'backgroundColor': '#D6EAF8',
                        'color': 'black',
                        'border': '2px solid blue'
                    }
                ]  
            ),
            html.Div(id='output')
        ])

            
        # Callback to update the graph based on the selected row
        @self.app.callback(
            Output('output', 'children'),
            [Input('table', 'selected_rows')]  # Listen to row selection
        )
        def display_selected_row(selected_rows):
            if selected_rows:
                selected_index = selected_rows[0]
                row = df.iloc[selected_index]
                config = USV_ENV_DESC_LIST[row['config_name']]
                env = USVEnvironment(config).update(row['best_solution'])
                self.data_queue.put(env)
                return f"Selected Row:\n{pprint.pformat(dict(sorted(row.to_dict().items())))}"
            return "No row selected"
        
    
    def run(self):
        self.app.run_server(debug=False, use_reloader=False)