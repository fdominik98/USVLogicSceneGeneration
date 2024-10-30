from typing import List
from model.data_parser import EvalDataParser
from model.environment.usv_environment import LoadedEnvironment
from evaluation.risk_evaluation import RiskVector
from evolutionary_computation.evaluation_data import EvaluationData

dp = EvalDataParser()
eval_datas : List[EvaluationData] = dp.load_dirs_merged_as_models()
skipped = 0
done = 0


# for eval_data in eval_datas:
#     path = eval_data.path
#     eval_data.path = None 
#     eval_data.save_to_json(path2=path)
#     done += 1
#     print(f'Config Group: {eval_data.config_group}. Done {done}, Skipped: {skipped} / {len(eval_datas)}')
# exit(0)#-------------------------------------------------------

START_FROM = 0

def info(data : EvaluationData):
    print(f'''Measurement: {data.measurement_name}, Algorithm: {data.algorithm_desc}, Config name: {data.config_name} 
            Config Group: {data.config_group}, Risk vector: {data.risk_vector}. Done {done}, Skipped: {skipped}, ({done + skipped} / {len(eval_datas)}, {(done + skipped) / len(eval_datas) * 100:.1f} %)''')

for i, eval_data in enumerate(eval_datas):
    if i < START_FROM:
        if eval_data.risk_vector is not None:
            done += 1
        else:
            skipped += 1
        print('Before start, skipped.')    
        info(eval_data)
        continue
    
    env = LoadedEnvironment(eval_data)
    if eval_data.best_fitness_index > 0.0:
        eval_data.risk_vector = None
        skipped += 1
        print('Not optimal solution, skipped.')
    else:    
        risk_vector = RiskVector(env)
        eval_data.risk_vector = risk_vector.risk_vector.tolist()
        done += 1
    eval_data.save_to_json()
    info(eval_data)
    