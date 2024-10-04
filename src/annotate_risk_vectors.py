from model.data_parser import EvalDataParser
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_config import EPSILON
from evaluation.risk_evaluation import RiskVector
from evolutionary_computation.evaluation_data import EvaluationData

CONFIG_GROUP = 'F4'
dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()
skipped = 0
done = 0



# for eval_data in eval_datas:
#     config = USV_ENV_DESC_LIST[eval_data.config_name]
#     env = USVEnvironment(config).update(eval_data.best_solution)
#     eval_data.config_group = CONFIG_GROUP
#     eval_data.vessel_number = config.vessel_num
#     eval_data.save_to_json(file_path=eval_data.path)
#     done += 1
#     print(f'Config Group: {CONFIG_GROUP}. Done {done}, Skipped: {skipped} / {len(eval_datas)}')
# exit(0)#-------------------------------------------------------

START_FROM = 0

def info(data : EvaluationData):
    print(f'''Measurement: {data.measurement_name}, Algorithm: {data.algorithm_desc}, Config name: {data.config_name} 
            Config Group: {CONFIG_GROUP}, Risk vector: {data.risk_vector}. Done {done}, Skipped: {skipped}, ({done + skipped} / {len(eval_datas)}, {(done + skipped) / len(eval_datas) * 100:.1f} %)''')

for i, eval_data in enumerate(eval_datas):
    if i < START_FROM:
        if eval_data.risk_vector is not None:
            done += 1
        else:
            skipped += 1
        print('Before start, skipped.')    
        info(eval_data)
        continue
    
    config = USV_ENV_DESC_LIST[eval_data.config_name]
    env = USVEnvironment(config).update(eval_data.best_solution)
    if eval_data.best_fitness_index >= EPSILON:
        eval_data.risk_vector = None
        eval_data.config_group = CONFIG_GROUP
        eval_data.risk_distance = None
        skipped += 1
        print('Not optimal solution, skipped.')
    else:    
        risk_vector = RiskVector(env)
        eval_data.risk_vector = risk_vector.risk_vector.tolist()
        eval_data.config_group = CONFIG_GROUP
        eval_data.risk_distance = risk_vector.distance
        done += 1
    eval_data.save_to_json(file_path=eval_data.path)
    info(eval_data)
    