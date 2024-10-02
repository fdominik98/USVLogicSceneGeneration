from model.data_parser import EvalDataParser
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_config import EPSILON
from evaluation.risk_evaluation import RiskVector

CONFIG_GROUP = 'F4'
dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()
skipped = 0
done = 0
for eval_data in eval_datas:
    if eval_data.best_fitness_index >= EPSILON:
        skipped += 1
        print('Not optimal solution, skipped.')
    else:        
        config = USV_ENV_DESC_LIST[eval_data.config_name]
        env = USVEnvironment(config).update(eval_data.best_solution)
        risk_vector = RiskVector(env)
        eval_data.risk_vector = risk_vector.risk_vector.tolist()
        eval_data.config_group = CONFIG_GROUP
        eval_data.save_to_json(file_path=eval_data.path)
        done += 1
        print(f'Config Group: {CONFIG_GROUP}, Risk vector: {risk_vector.risk_vector}. Done {done}, Skipped: {skipped} / {len(eval_datas)}')