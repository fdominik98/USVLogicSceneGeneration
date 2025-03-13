from datetime import datetime
import gc
from typing import Dict
import numpy as np
import random, scenic
from scenic.core.scenarios import Scenario
from concrete_level.models.concrete_vessel import ConcreteVessel
from concrete_level.models.vessel_state import VesselState
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.rejection_sampling.scenic_utils import generate_scene
from logical_level.models.vessel_types import ALL_VESSEL_TYPES, PassengerShip
from utils.evaluation_config import NUMBER_OF_RUNS, RANDOM_SEED, TIMEOUT, WARMUPS
from utils.file_system_utils import ASSET_FOLDER
import scenic


scenarios : Dict[int, Scenario] = {
    2 : scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/2vessel_scenario.scenic'),
    3 : scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/3vessel_scenario.scenic'),
    4 : scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/4vessel_scenario.scenic'),
    5 : scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/5vessel_scenario.scenic'),
    6 : scenic.scenarioFromFile(f'{ASSET_FOLDER}/scenic/6vessel_scenario.scenic')
}

for vessel_num, scenario in scenarios.items():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    scenario.resetExternalSampler()

    for i in range(NUMBER_OF_RUNS[vessel_num] + WARMUPS):
        eval_data = EvaluationData(timeout=TIMEOUT, random_seed=RANDOM_SEED)
        eval_data.config_group = 'scenic_distribution'
        eval_data.vessel_number = vessel_num
        eval_data.measurement_name = f'test_{vessel_num}_vessel_scenarios'
        eval_data.algorithm_desc = 'scenic_sampling'
        eval_data.scenario_name = f'{vessel_num}vessel'
        eval_data.timestamp = datetime.now().isoformat()   
        
        gc.collect()
        start_time = datetime.now()
        scene, num_iterations, runtime = generate_scene(scenario, TIMEOUT, 0, )
        
        eval_data.evaluation_time = runtime.total_seconds()
        
        eval_data.best_fitness_index = np.inf
        eval_data.best_fitness = (np.inf)
        builder = SceneBuilder()
        if scene is not None:
            for obj in scene.objects:
                if obj.is_vessel:
                    speed = np.linalg.norm(obj.velocity)
                    valid_types = [t for t in ALL_VESSEL_TYPES if t.do_match(obj.length, speed)]
                    vessel_type = PassengerShip() if obj.is_os else random.choice(valid_types)
                    builder.set_state(ConcreteVessel(obj.id, obj.is_os, obj.length, obj.length*4, vessel_type.max_speed, vessel_type.name),
                                    VesselState(obj.position[0], obj.position[1], speed, calculate_heading(obj.velocity[0], obj.velocity[1])))
            eval_data.best_fitness_index = 0.0
            eval_data.best_fitness = (0.0)
        eval_data.best_scene = builder.build()
        eval_data.number_of_generations = num_iterations
        
        if i >= WARMUPS:
            eval_data.save_as_measurement()