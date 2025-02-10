from concrete_level.data_parser import EvalDataParser
from evaluation.statistics_table_generator import StatisticsTableGenerator
from visualization.evaluation_plots.eval_plot_manager import EvalPlotManager

dp = EvalDataParser()
eval_datas = dp.load_dirs_merged_as_models()
EvalPlotManager(eval_datas)

generator = StatisticsTableGenerator(eval_datas)
generator.generate_runtime_summary_table()
generator.generate_stat_sign_table()