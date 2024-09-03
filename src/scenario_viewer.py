from typing import List
from genetic_algorithms.evaluation_data import EvaluationData
from visualization.colreg_plot import ColregPlot
from visualization.data_parser import EvalDataParser
from model.usv_env_desc_list import USV_ENV_DESC_LIST
from model.usv_environment import USVEnvironment

while(True):
    dp = EvalDataParser()
    data_models : List[EvaluationData] = dp.load_data_models()
    
    if len(data_models) == 0:
        exit(0)

    config = USV_ENV_DESC_LIST[data_models[0].config_name]
    env = USVEnvironment(config).update(data_models[0].best_solution)
    ColregPlot(env)
        
        