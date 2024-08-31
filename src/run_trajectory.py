from genetic_algorithms.evaluation_data import EvaluationData
from trajectory_planning.trajectory_data import TrajectoryData
from visualization.colreg_plot import ColregPlot
from visualization.data_parser import EvalDataParser, TrajDataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment

while(True):
    tdp = TrajDataParser()
    edp = EvalDataParser()
    
    traj_data_models : list[TrajectoryData] = tdp.load_data_models()
    
    if len(traj_data_models) == 0:
        exit(0)
    
    eval_data_models : list[EvaluationData] = edp.load_data_models_from_files([traj_data_models[0].env_path])
    
    config = USV_ENV_DESC_LIST[eval_data_models[0].config_name]
    env = USVEnvironment(config).update(eval_data_models[0].best_solution)
    ColregPlot(env, trajectories=traj_data_models[0].trajectories)
        
        