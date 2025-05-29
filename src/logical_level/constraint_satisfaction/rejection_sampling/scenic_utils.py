import inspect
from itertools import chain
import os
from typing import Any, List, Tuple
import numpy as np
import random, scenic
from scenic.core.scenarios import Scenario as ScenicScenario
from logical_level.constraint_satisfaction.aggregates import Aggregate
from utils.math_utils import calculate_heading
from utils.file_system_utils import SCENIC_FOLDER
import global_config

import scenic
from scenic.core.distributions import (
    RejectionException,
    Samplable,
    needsSampling,
)
from scenic.core.errors import optionallyDebugRejection

def generate_scene(scenario : ScenicScenario, aggregate : Aggregate, first_solution, feedback=None) -> Tuple[List[float], str]:
    # choose which custom requirements will be enforced for this sample
    # for req in scenario.userRequirements:
    #     if random.random() <= req.prob:
    #         req.active = True
    #     else:
    #         req.active = False

    # do rejection sampling until requirements are satisfied
    rejection = ''
    try:
        sample = Samplable.sampleAll(scenario.dependencies)
        # Ensure nothing else is lazy
        for obj in scenario.objects:
            sampledObj = sample[obj]
            assert not needsSampling(sampledObj)
        # Check validity of sample, storing state so that
        # checker heuristics don't affect determinism
        # rand_state, np_state = random.getstate(), np.random.get_state()
        #rejection = scenario.checker.checkRequirements(sample)
        solution = calculate_solution(scenario._makeSceneFromSample(sample))
        penalty = aggregate.derive_penalty(solution)
        if not penalty.is_zero:
            rejection += 'Requirements do not hold.'
            # print(penalty.pretty_info())
            
    except RejectionException as e:
        optionallyDebugRejection(e)
        rejection = str(e)
        solution = first_solution
    
    # random.setstate(rand_state)
    # np.random.set_state(np_state)

    # if rejection is not None:
    #     optionallyDebugRejection()

    # # obtained a valid sample; assemble a scene from it
    # scene = scenario._makeSceneFromSample(sample)
    return solution, rejection
    

def scenic_scenario(os_id, ts_ids, obst_ids, length_map, radius_map, possible_distances_map, min_distance_map, vis_distance_map, bearing_map, verbose=False) -> ScenicScenario:
    base_path = f'{SCENIC_FOLDER}/scenic_base.scenic'
    if not os.path.exists(base_path):
        raise FileNotFoundError(base_path)
    with open(base_path, 'r') as file:
        base_code = file.read()
    
    scenic_code = generate_scenario_code(base_code, os_id, ts_ids, obst_ids, length_map, radius_map, possible_distances_map, min_distance_map, vis_distance_map, bearing_map)
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
    
def calculate_solution(scene: ScenicScenario) -> List[float]:            
    actors = sorted([obj for obj in scene.objects if obj.is_actor], key=lambda obj: obj.id)
    solution = list(chain.from_iterable([object_to_individual(obj) for obj in actors]))
    return solution


def generate_scenario_code(base_code, os_id, ts_ids, obst_ids, length_map, radius_map, possible_distances_map, min_distance_map, vis_distance_map, bearing_map):
    ts_infos_assignments = "\n".join(
        [f"ts{i} = ts_infos.pop(0)" for i in ts_ids]
    )
    
    obst_infos_assignments = "\n".join(
        [f"obst{i} = obst_infos.pop(0)" for i in obst_ids]
    )
    
    code = "\n".join(
         [inspect.getsource(global_config),
         base_code,
         f"ts_infos, obst_infos = create_scenario(os_id = {os_id}, ts_ids={ts_ids}, obst_ids={obst_ids}, length_map={length_map}, radius_map={radius_map}, possible_distances_map={possible_distances_map}, min_distance_map={min_distance_map}, vis_distance_map={vis_distance_map}, bearing_map={bearing_map})",
         ts_infos_assignments,
         obst_infos_assignments,
        ]        
    )
    return code.strip()
