from typing import Optional
from visualization.dash_thread import DashThread
from visualization.colreg_scenarios.colreg_plot_manager import ColregPlotManager
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST

dash_thread = DashThread()
dash_thread.start()

colreg_plot_manager : Optional[ColregPlotManager] = None

# Main loop to listen for data and create windows
while dash_thread.is_alive():
    env = dash_thread.data_queue.get()  # Wait for data with a timeout
    colreg_plot_manager = ColregPlotManager(env)