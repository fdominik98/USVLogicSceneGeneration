from typing import List
from concrete_level.models.trajectory_manager import TrajectoryManager
from concrete_level.trajectory_generation.trajectory_data import TrajectoryData
from concrete_level.data_parser import TrajDataParser
from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager

while(True):
    tdp = TrajDataParser()
    traj_data_models : List[TrajectoryData] = tdp.load_data_models()
    
    if len(traj_data_models) == 0:
        exit(0)
    
    ScenarioPlotManager(TrajectoryManager(traj_data_models[0].trajectories))
        
        