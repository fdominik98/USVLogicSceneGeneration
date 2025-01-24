import numpy as np
import random, scenic
from scenic.core.scenarios import Scenario
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.trajectory_manager import TrajectoryManager
from concrete_level.models.vessel_state import VesselState
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from utils.file_system_utils import ASSET_FOLDER
from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager

random.seed(12345)
scenario : Scenario = scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/scenario.scenic')
scenes, numIterations = scenario.generateBatch(1, verbosity=1)

vessel1 = scenes[0].objects[0]
vessel2 = scenes[0].objects[1]
builder = SceneBuilder()
for obj in scenes[0].objects:
    if obj.is_vessel:
        builder.set_state(ConcreteVessel(obj.id, obj.is_os, obj.l, obj.r, obj.max_speed),
                        VesselState(obj.p[0], obj.p[1], obj.sp, obj.h))

ScenarioPlotManager(TrajectoryManager(builder.build()))
