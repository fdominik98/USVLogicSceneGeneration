from datetime import datetime
import gc
import os
import numpy as np
import random, scenic
from scenic.core.scenarios import Scenario
from concrete_level.models.concrete_scene import ConcreteScene
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.trajectory_manager import TrajectoryManager
from concrete_level.models.vessel_state import VesselState
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from logical_level.models.vessel_types import ALL_VESSEL_TYPES, PassengerShip
from utils.file_system_utils import ASSET_FOLDER
from visualization.colreg_scenarios.scenario_plot_manager import ScenarioPlotManager

WARMUPS = 2
RANDOM_SEED = 1234
TIMEOUT = 240
VESSEL_NUM = 2

def save_eval_data(eval_data : EvaluationData):
    asset_folder = f'{ASSET_FOLDER}/gen_data/{eval_data.measurement_name}/{eval_data.config_group}/{eval_data.algorithm_desc}'
    if not os.path.exists(asset_folder):
        os.makedirs(asset_folder)
    file_path=f"{asset_folder}/{eval_data.scenario_name}_{eval_data.timestamp.replace(':','-')}.json"
    eval_data.path = file_path
    eval_data.save_to_json()
    
def calculate_heading(vx, vy):
    heading_radians = np.arctan2(vy, vx)
    return heading_radians

scenario : Scenario = scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/scenario.scenic', params={'vessel_num' : VESSEL_NUM})
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
scenario.resetExternalSampler()

for i in range(1000):
    eval_data = EvaluationData(timeout=TIMEOUT, random_seed=RANDOM_SEED)
    eval_data.config_group = 'scenic_distribution'
    eval_data.vessel_number = VESSEL_NUM
    eval_data.measurement_name = f'test_{VESSEL_NUM}_vessel_scenarios'
    eval_data.algorithm_desc = 'scenic_sampling'
    eval_data.scenario_name = f'{VESSEL_NUM}vessel'
    eval_data.timestamp = datetime.now().isoformat()   
    
    gc.collect()
    start_time = datetime.now()
    scenes, numIterations = scenario.generateBatch(1, verbosity=1)
    
    eval_data.evaluation_time = (datetime.now() - start_time).total_seconds()
    
    builder = SceneBuilder()
    for obj in scenes[0].objects:
        if obj.is_vessel:
            speed = np.linalg.norm(obj.velocity)
            valid_types = [t for t in ALL_VESSEL_TYPES if t.do_match(obj.length, speed)]
            vessel_type = PassengerShip() if obj.is_os else random.choice(valid_types)
            builder.set_state(ConcreteVessel(obj.id, obj.is_os, obj.length, obj.length*4, obj.max_speed, vessel_type.name),
                            VesselState(obj.position[0], obj.position[1], speed, calculate_heading(obj.velocity[0], obj.velocity[1])))
    eval_data.best_scene = builder.build()
    eval_data.best_fitness = (0)
    eval_data.number_of_generations = numIterations
    eval_data.best_fitness_index = 0.0
    
    save_eval_data(eval_data)
    
    #ScenarioPlotManager(TrajectoryManager(builder.build()))
