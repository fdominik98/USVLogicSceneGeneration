from concrete_level.data_parser import EvalDataParser
from concrete_level.models.trajectory_manager import TrajectoryManager
from concrete_level.trajectory_generation.trajectory_generator import TrajectoryGenerator
from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager


dp = EvalDataParser()
data_models = dp.load_data_models()

if len(data_models) == 0:
    exit(0)

eval_data = data_models[0]
trajectory_manager = TrajectoryManager(eval_data.best_scene)
ScenarioPlotManager(trajectory_manager)

traj_gen = TrajectoryGenerator(eval_data, trajectory_manager.scenario)

ScenarioPlotManager(TrajectoryManager(traj_gen.trajectories))