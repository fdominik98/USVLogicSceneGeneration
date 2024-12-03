from typing import Dict, List
from model.data_parser import EvalDataParser
from model.environment.usv_environment import LoadedEnvironment
from evaluation.risk_evaluation import RiskVector
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from model.environment.usv_config import KNOT_TO_MS_CONVERSION, OWN_VESSEL_STATES, VARIABLE_NUM
from model.environment.functional_models.model_utils import _OS, TS1, TS2, TS3, TS4, TS5
from model.vessel import Vessel, VesselDesc
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from concrete_level.model.concrete_vessel import ConcreteVessel
from concrete_level.model.vessel_state import VesselState

dp = EvalDataParser()
eval_datas : List[EvaluationData] = dp.load_dirs_merged_as_models()
skipped = 0
done = 0


# for eval_data in eval_datas:    
#     all_vessels_descs = [_OS, TS1, TS2, TS3, TS4, TS5]
#     states = OWN_VESSEL_STATES + eval_data.best_solution
#     vessel_descs = all_vessels_descs[:eval_data.vessel_number]
#     sb = SceneBuilder()
#     for id, vessel_desc in enumerate(vessel_descs):
#             vessel = Vessel(vessel_desc)
#             vessel.update(states[id * VARIABLE_NUM],
#                             states[id * VARIABLE_NUM + 1],
#                             states[id * VARIABLE_NUM + 2],
#                             states[id * VARIABLE_NUM + 3],
#                             states[id * VARIABLE_NUM + 4])
#             sb.set_state(ConcreteVessel(vessel.id, vessel.l, vessel.r, 30 * KNOT_TO_MS_CONVERSION), VesselState(vessel.p[0], vessel.p[1], vessel.speed, vessel.heading))
            
#     scene = sb.build()   
    
#     eval_data2 = EvaluationData2(algorithm_desc=eval_data.algorithm_desc
#         ,config_name=eval_data.config_name, random_seed=eval_data. random_seed, evaluation_time=eval_data. evaluation_time
#         ,number_of_generations=eval_data.number_of_generations, population_size=eval_data. population_size
#         ,num_parents_mating=eval_data.num_parents_mating, best_fitness=eval_data.best_fitness, mutate_eta=eval_data.mutate_eta
#         ,mutate_prob=eval_data.mutate_prob, crossover_eta=eval_data.crossover_eta
#         ,crossover_prob=eval_data.crossover_prob, error_message=eval_data. error_message
#         ,timestamp=eval_data.timestamp, measurement_name =eval_data. measurement_name
#         ,path=eval_data. path, timeout=eval_data.timeout, init_method = eval_data.init_method
#         ,c_1=eval_data. c_1, c_2=eval_data. c_2, w=eval_data.w, best_fitness_index =eval_data. best_fitness_index
#         ,aggregate_strat =eval_data. aggregate_strat, config_group = eval_data.config_group, best_scene=scene)
    
#     eval_data2.save_to_json(path2=eval_data.path)
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
    
    env = LoadedEnvironment(eval_data)
    if eval_data.best_fitness_index > 0.0:
        eval_data.best_scene.danger_sector = None
        skipped += 1
        print('Not optimal solution, skipped.')
    else:    
        risk_vector = RiskVector(env)
        eval_data.best_scene.dcpa = risk_vector.risk_vector[0]
        eval_data.best_scene.tcpa = risk_vector.risk_vector[1]
        eval_data.best_scene.danger_sector = risk_vector.risk_vector[2]
        eval_data.best_scene.proximity_index = risk_vector.risk_vector[3]
        done += 1
    eval_data.save_to_json()
    info(eval_data)
    