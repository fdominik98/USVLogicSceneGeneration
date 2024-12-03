from collections import defaultdict
from typing import Dict, List
from model.data_parser import EvalDataParser
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from visualization.algo_evaluation.eval_plot_manager import EvalPlotManager

dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()
EvalPlotManager(eval_datas)