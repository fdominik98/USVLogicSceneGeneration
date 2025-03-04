from datetime import datetime
import os
from typing import Dict
import numpy as np
import random, scenic
from scenic.core.scenarios import Scenario
from utils.file_system_utils import ASSET_FOLDER

import scenic
from scenic.core.distributions import (
    RejectionException,
    Samplable,
    needsSampling,
)
from scenic.core.errors import optionallyDebugRejection

def generate_scene(scenario : Scenario, timeout, verbosity, feedback=None):
    # choose which custom requirements will be enforced for this sample
    for req in scenario.userRequirements:
        if random.random() <= req.prob:
            req.active = True
        else:
            req.active = False

    # do rejection sampling until requirements are satisfied
    rejection = True
    iterations = 0
    start_time = datetime.now()
    while rejection is not None:
        if iterations > 0:  # rejected the last sample
            if verbosity >= 2:
                print(f"  Rejected sample {iterations} because of {rejection}")
            if scenario.externalSampler is not None:
                feedback = scenario.externalSampler.rejectionFeedback
        if (datetime.now() - start_time).total_seconds() >= timeout:
            print(f"Sampling reached timeout.")
            return None, iterations, datetime.now() - start_time
        iterations += 1
        try:
            if scenario.externalSampler is not None:
                scenario.externalSampler.sample(feedback)
            sample = Samplable.sampleAll(scenario.dependencies)
        except RejectionException as e:
            optionallyDebugRejection(e)
            rejection = e
            continue
        rejection = None

        # Ensure nothing else is lazy
        for obj in scenario.objects:
            sampledObj = sample[obj]
            assert not needsSampling(sampledObj)

        # Check validity of sample, storing state so that
        # checker heuristics don't affect determinism
        rand_state, np_state = random.getstate(), np.random.get_state()
        rejection = scenario.checker.checkRequirements(sample)
        random.setstate(rand_state)
        np.random.set_state(np_state)

        if rejection is not None:
            optionallyDebugRejection()

    # obtained a valid sample; assemble a scene from it
    scene = scenario._makeSceneFromSample(sample)
    return scene, iterations, datetime.now() - start_time
    

SCENIC_SCENARIOS : Dict[int, str] = {
    2 : f'{ASSET_FOLDER}/scenic/2vessel_scenario.scenic',
    3 : f'{ASSET_FOLDER}/scenic/3vessel_scenario.scenic',
    4 : f'{ASSET_FOLDER}/scenic/4vessel_scenario.scenic',
    5 : f'{ASSET_FOLDER}/scenic/5vessel_scenario.scenic',
    6 : f'{ASSET_FOLDER}/scenic/6vessel_scenario.scenic'
}

def scenic_scenario(vessel_number, vis_distance_map = {}, length_map = {}, bearing_map={}) -> Scenario:
    base_path = f'{ASSET_FOLDER}/scenic/scenic_base.scenic'
    if not os.path.exists(base_path):
        raise FileNotFoundError(base_path)
    with open(base_path, 'r') as file:
        base = file.read()
    
    
    if not os.path.exists(SCENIC_SCENARIOS[vessel_number]):
        raise FileNotFoundError(SCENIC_SCENARIOS[vessel_number])
    with open(SCENIC_SCENARIOS[vessel_number], 'r') as file:
        scenario_path = file.read()
    
    content = f'vis_distance_map = {str(vis_distance_map)}\nlength_map = {str(length_map)}\nbearing_map = {str(bearing_map)}\n{base}\n{scenario_path}' 
    return scenic.scenarioFromString(content)
    
    #return scenic.scenarioFromFile(SCENIC_SCENARIOS[vessel_number], params={'vis_distance_map' : vis_distance_map, 'length_map' : length_map})

# for vessel_num in SCENIC_SCENARIOS.keys():
#     scenario = scenic_scenario(vessel_num)
#     random.seed(RANDOM_SEED)
#     np.random.seed(RANDOM_SEED)
#     scenario.resetExternalSampler()

#     for i in range(NUMBER_OF_RUNS + WARMUPS):
#         eval_data = EvaluationData(timeout=TIMEOUT, random_seed=RANDOM_SEED)
#         eval_data.config_group = 'RS'
#         eval_data.vessel_number = vessel_num
#         eval_data.measurement_name = f'test_{vessel_num}_vessel_scenarios'
#         eval_data.algorithm_desc = 'scenic_sampling'
#         eval_data.scenario_name = f'{vessel_num}vessel'
#         eval_data.timestamp = datetime.now().isoformat()   
        
#         gc.collect()
#         start_time = datetime.now()
#         scene, num_iterations, runtime = generate_scene(scenario, TIMEOUT, 0, )
        
#         eval_data.evaluation_time = runtime.total_seconds()
        
#         eval_data.best_fitness_index = np.inf
#         eval_data.best_fitness = (np.inf)
#         builder = SceneBuilder()
#         if scene is not None:
#             for obj in scene.objects:
#                 if obj.is_vessel:
#                     speed = np.linalg.norm(obj.velocity)
#                     valid_types = [t for t in ALL_VESSEL_TYPES if t.do_match(obj.length, speed)]
#                     vessel_type = PassengerShip() if obj.is_os else random.choice(valid_types)
#                     builder.set_state(ConcreteVessel(obj.id, obj.is_os, obj.length, obj.length*4, vessel_type.max_speed, vessel_type.name),
#                                     VesselState(obj.position[0], obj.position[1], speed, calculate_heading(obj.velocity[0], obj.velocity[1])))
#             eval_data.best_fitness_index = 0.0
#             eval_data.best_fitness = (0.0)
#         eval_data.best_scene = builder.build()
#         eval_data.number_of_generations = num_iterations
        
#         if i >= WARMUPS:
#             eval_data.save_as_measurement()
    