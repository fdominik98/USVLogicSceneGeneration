from datetime import datetime
from itertools import chain
import os
from typing import Any, Dict, List, Tuple
import numpy as np
import random, scenic
from scenic.core.scenarios import Scenario
from utils.asv_utils import calculate_heading
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
    empty_region = False
    while rejection is not None:
        if iterations > 0:  # rejected the last sample
            if verbosity >= 2:
                print(f"  Rejected sample {iterations} because of {rejection}")
            if scenario.externalSampler is not None:
                feedback = scenario.externalSampler.rejectionFeedback
                
                
        if (datetime.now() - start_time).total_seconds() >= timeout:
            print(f"Sampling reached timeout.")
            return None, iterations, datetime.now() - start_time, empty_region
        iterations += 1
        try:
            if scenario.externalSampler is not None:
                scenario.externalSampler.sample(feedback)
            sample = Samplable.sampleAll(scenario.dependencies)
        except RejectionException as e:
            optionallyDebugRejection(e)
            rejection = e
            if rejection.args[0] == 'sampling empty Region':
                empty_region = True
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
    return scene, iterations, datetime.now() - start_time, empty_region
    

SCENIC_SCENARIOS : Dict[Tuple[int, int], str] = {
    (2, 0) : f'{ASSET_FOLDER}/scenic/2vessel_0obstacle_scenario.scenic',
    (3, 0) : f'{ASSET_FOLDER}/scenic/3vessel_0obstacle_scenario.scenic',
    (4, 0) : f'{ASSET_FOLDER}/scenic/4vessel_0obstacle_scenario.scenic',
    (5, 0) : f'{ASSET_FOLDER}/scenic/5vessel_0obstacle_scenario.scenic',
    (6, 0) : f'{ASSET_FOLDER}/scenic/6vessel_0obstacle_scenario.scenic'
}

def scenic_scenario(vessel_number : int, obstacle_number : int, length_map, vis_distance_map = {}, bearing_map={}) -> Scenario:
    actor_number_by_type = (vessel_number, obstacle_number)
    
    base_path = f'{ASSET_FOLDER}/scenic/scenic_base.scenic'
    if not os.path.exists(base_path):
        raise FileNotFoundError(base_path)
    with open(base_path, 'r') as file:
        base = file.read()
    
    
    if not os.path.exists(SCENIC_SCENARIOS[actor_number_by_type]):
        raise FileNotFoundError(SCENIC_SCENARIOS[actor_number_by_type])
    with open(SCENIC_SCENARIOS[actor_number_by_type], 'r') as file:
        scenario_path = file.read()
    
    content = f'vis_distance_map = {str(vis_distance_map)}\nlength_map = {str(length_map)}\nbearing_map = {str(bearing_map)}\n{base}\n{scenario_path}' 
    return scenic.scenarioFromString(content)
    
    
def calculate_solution(population: List[float], scene: Any) -> Tuple[List[float]]:
    if scene is None:
        solution = population
    else:            
        objects = sorted([obj for obj in scene.objects if obj.is_vessel], key=lambda obj: obj.id)
        solution = list(chain.from_iterable([[obj.position[0],
                        obj.position[1],
                        calculate_heading(obj.velocity[0], obj.velocity[1]),
                        obj.length, np.linalg.norm(obj.velocity)] for obj in objects]))
    return solution
