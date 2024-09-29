from collections import defaultdict
from typing import Dict, List
from model.data_parser import EvalDataParser
from evolutionary_computation.evaluation_data import EvaluationData
from visualization.algo_evaluation.eval_plot_manager import EvalPlotManager

dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()
# Assuming the objects have these attributes: measurement_name, algorithm_desc, config_name, best_fitness
eval_times : Dict[str, Dict[str, List[float]]] = defaultdict(lambda : defaultdict(lambda : []))
successes : Dict[str, Dict[str, List[int]]] = defaultdict(lambda : defaultdict(lambda : []))
measurements : Dict[str, Dict[str, List[EvaluationData]]] = defaultdict(lambda : defaultdict(lambda : []))
# Populate the nested dictionary
for eval_data in eval_datas:
    measurements[eval_data.measurement_name][eval_data.algorithm_desc].append(eval_data)
    
EvalPlotManager(measurements)