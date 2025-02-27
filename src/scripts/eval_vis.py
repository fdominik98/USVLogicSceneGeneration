from concrete_level.data_parser import EvalDataParser
from visualization.evaluation_plots.eval_plot_manager import EvalPlotManager

dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()

EvalPlotManager(eval_datas)