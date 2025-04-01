import inspect
from datetime import datetime
from itertools import chain, combinations, product
import os
from typing import Any, List, Tuple
import numpy as np
import random, scenic
from scenic.core.scenarios import Scenario
from utils.math_utils import calculate_heading
from utils.file_system_utils import SCENIC_FOLDER
import global_config
from utils import math_utils

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
    

def scenic_scenario(os_id, ts_ids, obst_ids, length_map, radius_map, vis_distance_map = {}, bearing_map={}, verbose=False) -> Scenario:
    base_path = f'{SCENIC_FOLDER}/scenic_base.scenic'
    if not os.path.exists(base_path):
        raise FileNotFoundError(base_path)
    with open(base_path, 'r') as file:
        base_code = file.read()
    
    scenic_code = generate_scenario_code(base_code, os_id, ts_ids, obst_ids, length_map, radius_map, vis_distance_map, bearing_map)
    if verbose:
        with open(f'{SCENIC_FOLDER}/test_gen.scenic', 'w') as file:
            file.write(scenic_code)
    return scenic.scenarioFromString(scenic_code)
    
  
def vessel_object_to_individual(obj):
    return [obj.position[0], obj.position[1], calculate_heading(obj.velocity[0], obj.velocity[1]), obj.length, np.linalg.norm(obj.velocity)]
        
def obstacle_object_to_individual(obj):
    return [obj.position[0], obj.position[1], obj.area_radius]

def object_to_individual(obj):
    return vessel_object_to_individual(obj) if obj.is_vessel else obstacle_object_to_individual(obj)
    
def calculate_solution(population: List[float], scene: Any) -> Tuple[List[float]]:
    if scene is None:
        solution = population
    else:            
        actors = sorted([obj for obj in scene.objects if obj.is_actor], key=lambda obj: obj.id)
        solution = list(chain.from_iterable([object_to_individual(obj) for obj in actors]))
    return solution


def generate_scenario_code(base_code, os_id, ts_ids, obst_ids, length_map, radius_map, vis_distance_map, bearing_map):
    ts_infos_assignments = "\n".join(
        [f"ts{i}, prop{i} = ts_infos.pop(0)\nrequire prop{i}.check_at_vis_may_collide()" for i in ts_ids]
    )
    
    obst_infos_assignments = "\n".join(
        [f"obst{i}, prop{i} = obst_infos.pop(0)\nrequire prop{i}.check_at_vis_may_collide()" for i in obst_ids]
    )
    
    ts_pair_constraints = "\n".join(
        [f"prop_ts_ts{k} = new VesselToVesselProperties with val1 ts{i}, with val2 ts{j}\nrequire prop_ts_ts{k}.check_out_vis_or_may_not_collide()"
         for k, (i, j) in enumerate(combinations(ts_ids, 2))]
    )
    
    ts_obst_pair_constraints = "\n".join(
        [f"prop_obst_ts{k} = new ObstacleToVesselProperties with val1 obst{i}, with val2 ts{j}\nrequire prop_obst_ts{k}.check_out_vis_or_may_not_collide()"
         for k, (i, j) in enumerate(product(obst_ids, ts_ids))]
    )
    
    code = "\n".join(
        [inspect.getsource(math_utils),
         inspect.getsource(global_config),
         base_code,
         f"ts_infos, obst_infos = create_scenario(os_id = {os_id}, ts_ids={ts_ids}, obst_ids={obst_ids}, length_map={length_map}, radius_map={radius_map}, vis_distance_map={vis_distance_map}, bearing_map={bearing_map})",
         ts_infos_assignments,
         obst_infos_assignments,
         ts_pair_constraints,
         ts_obst_pair_constraints
        ]        
    )
    return code.strip()
