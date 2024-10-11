from typing import List
from evolutionary_computation.evaluation_data import EvaluationData
from evaluation.risk_evaluation import RiskVector
from visualization.colreg_scenarios.colreg_plot_manager import ColregPlotManager
from model.data_parser import EvalDataParser
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST
from model.environment.usv_environment import USVEnvironment

while(True):
    dp = EvalDataParser()
    data_models : List[EvaluationData] = dp.load_data_models()
    
    if len(data_models) == 0:
        exit(0)

    data = data_models[0]
    config = USV_ENV_DESC_LIST[data.config_name]
    env = USVEnvironment(config).update(data_models[0].best_solution)
    
    risk_vector = RiskVector(env)
    print(risk_vector.risk_vector)
    ColregPlotManager(env)
        
        