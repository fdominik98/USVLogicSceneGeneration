from typing import List
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from concrete_level.data_parser import EvalDataParser
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from evaluation.risk_evaluation import RiskVector
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData

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
    print(f'''Measurement: {data.measurement_name}, Algorithm: {data.algorithm_desc}, Config name: {data.scenario_name} 
            Config Group: {data.config_group}. Done {done}, Skipped: {skipped}, ({done + skipped} / {len(eval_datas)}, {(done + skipped) / len(eval_datas) * 100:.1f} %)''')

for i, eval_data in enumerate(eval_datas):
    
    if i < START_FROM:
        if eval_data.best_scene.has_functional_hash:
            done += 1
        else:
            skipped += 1
        print('Before start, skipped.')    
        info(eval_data)
        continue
    
    if not eval_data.is_valid:
        skipped += 1
        print('Not optimal solution, skipped.')
    else:    
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
        done += 1
        eval_data.save_to_json()
    info(eval_data)
    