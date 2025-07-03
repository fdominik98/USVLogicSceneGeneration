import json
from typing import List
from concrete_level.concrete_scene_abstractor import ConcreteSceneAbstractor
from concrete_level.data_parser import EvalDataParser
from concrete_level.models.multi_level_scenario import MultiLevelScenario
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from evaluation.risk_evaluation import RiskVector
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from utils.file_system_utils import GEN_DATA_FOLDER

dp = EvalDataParser()
eval_datas : List[EvaluationData] = dp.load_dirs_merged_as_models()

# Save to JSON file
with open(f"{GEN_DATA_FOLDER}/compressed.json", "w") as f:
    json.dump([e.to_dict() for e in eval_datas], f, indent=2)