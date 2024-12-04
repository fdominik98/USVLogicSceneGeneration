from typing import Dict, List
from concrete_level.data_parser import EvalDataParser
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from evaluation.risk_evaluation import RiskVector
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData

dp = EvalDataParser()
eval_datas : List[EvaluationData] = dp.load_dirs_merged_as_models()
skipped = 0
done = 0

# for eval_data in eval_datas:    
#     pass    
#     eval_data.save_to_json(path2=eval_data.path)
#     done += 1
#     print(f'Config Group: {eval_data.config_group}. Done {done}, Skipped: {skipped} / {len(eval_datas)}')
# exit(0)#-------------------------------------------------------

START_FROM = 0

def info(data : EvaluationData):
    print(f'''Measurement: {data.measurement_name}, Algorithm: {data.algorithm_desc}, Config name: {data.config_name} 
            Config Group: {data.config_group}. Done {done}, Skipped: {skipped}, ({done + skipped} / {len(eval_datas)}, {(done + skipped) / len(eval_datas) * 100:.1f} %)''')

for i, eval_data in enumerate(eval_datas):
    if i < START_FROM:
        if eval_data.best_scene.danger_sector is not None:
            done += 1
        else:
            skipped += 1
        print('Before start, skipped.')    
        info(eval_data)
        continue
    
    logical_scenario = LogicalScenarioBuilder().build_from_concrete(eval_data.best_scene, eval_data.init_method)
    if eval_data.best_fitness_index > 0.0:
        eval_data.best_scene.danger_sector = None
        skipped += 1
        print('Not optimal solution, skipped.')
    else:    
        risk_vector = RiskVector(logical_scenario)
        eval_data.best_scene.dcpa = risk_vector.risk_vector[0]
        eval_data.best_scene.tcpa = risk_vector.risk_vector[1]
        eval_data.best_scene.danger_sector = risk_vector.risk_vector[2]
        eval_data.best_scene.proximity_index = risk_vector.risk_vector[3]
        done += 1
    eval_data.save_to_json()
    info(eval_data)
    