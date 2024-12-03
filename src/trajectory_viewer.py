from typing import List
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from visualization.colreg_scenarios.colreg_plot_manager import ColregPlotManager
from trajectory_planning.model.trajectory_data import TrajectoryData
from model.data_parser import EvalDataParser, TrajDataParser
from model.environment.usv_environment import LoadedEnvironment

while(True):
    tdp = TrajDataParser()
    edp = EvalDataParser()
    
    traj_data_models : List[TrajectoryData] = tdp.load_data_models()
    
    if len(traj_data_models) == 0:
        exit(0)
    
    eval_data_models : List[EvaluationData] = edp.load_data_models_from_files([traj_data_models[0].env_path])
    
    data = eval_data_models[0]
    env = LoadedEnvironment(eval_data_models[0])
    ColregPlotManager(env, trajectories=traj_data_models[0].trajectories)
        
        