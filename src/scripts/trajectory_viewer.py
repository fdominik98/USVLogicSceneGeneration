from typing import List
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager
from concrete_level.trajectory_generation.trajectory_data import TrajectoryData
from concrete_level.data_parser import EvalDataParser, TrajDataParser

while(True):
    tdp = TrajDataParser()
    edp = EvalDataParser()
    
    traj_data_models : List[TrajectoryData] = tdp.load_data_models()
    
    if len(traj_data_models) == 0:
        exit(0)
    
    eval_data_models : List[EvaluationData] = edp.load_data_models_from_files([traj_data_models[0].logical_scenario_path])
    
    data = eval_data_models[0]
    # logical_scenario= LoadedEnvironment(eval_data_models[0])
    # ScenarioPlotManager(logical_scenario, trajectories=traj_data_models[0].trajectories)
        
        