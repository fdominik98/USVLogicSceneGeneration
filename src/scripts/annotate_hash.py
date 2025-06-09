from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, cpu_count
import random
import time
from typing import List

import numpy as np
from tqdm import tqdm
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from concrete_level.data_parser import EvalDataParser
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData

# for eval_data in eval_datas:    
#     pass    
#     eval_data.save_to_json(path2=eval_data.path)
#     done += 1
#     print(f'Config Group: {eval_data.config_group}. Done {done}, Skipped: {skipped} / {len(eval_datas)}')
# exit(0)#-------------------------------------------------------

def info(data : EvaluationData, done : int, skipped : int, total_eval_datas : int):
    print(f'''Measurement: {data.measurement_name}, Algorithm: {data.algorithm_desc}, Config name: {data.scenario_name} 
            Config Group: {data.config_group}. Done {done}, Skipped: {skipped}, ({done + skipped} / {total_eval_datas}, {(done + skipped) / total_eval_datas * 100:.1f} %)''')

def annotate_hash(eval_data : EvaluationData):
    # skipped = 0
    # done = 0
    if not eval_data.is_valid:
        return
        # skipped += 1
        # print('Not optimal solution, skipped.')
    scenario = ConcreteSceneAbstractor.get_abstractions_from_eval(eval_data)
    fsm_level_hash = scenario.functional_scenario.fsm_shape_hash()
    fec_level_hash = scenario.functional_scenario.fec_shape_hash()
    is_relevant_by_fec = scenario.functional_scenario.is_relevant_by_fec
    is_relevant_by_fsm = scenario.functional_scenario.is_relevant_by_fsm
    is_ambiguous_by_fec = scenario.functional_scenario.is_ambiguous_by_fec
    is_ambiguous_by_fsm = scenario.functional_scenario.is_ambiguous_by_fsm
    eval_data.best_scene = SceneBuilder(eval_data.best_scene).build(
                                                    first_level_hash=fsm_level_hash,
                                                    second_level_hash=fec_level_hash,
                                                    is_relevant_by_fec=is_relevant_by_fec,
                                                    is_relevant_by_fsm=is_relevant_by_fsm,
                                                    is_ambiguous_by_fec=is_ambiguous_by_fec,
                                                    is_ambiguous_by_fsm=is_ambiguous_by_fsm)
    # done += 1
    eval_data.save_to_json()
    # info(eval_data, done, skipped, len(eval_datas))
    
def main():
    dp = EvalDataParser()
    eval_datas : List[EvaluationData] = dp.load_dirs_merged_as_models()
    
    # random.seed(time.time())
    # random.shuffle(eval_datas)

    # core_count = cpu_count()

    # eval_data_batches = np.array_split(eval_datas, core_count)
    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(annotate_hash, eval_datas), total=len(eval_datas), desc="Hashing eval datas"))
            
if __name__ == '__main__':
    main()