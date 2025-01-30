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

import scenic
from scenic.core.distributions import (
    RejectionException,
    Samplable,
    needsSampling,
)
from scenic.core.errors import optionallyDebugRejection


WARMUPS = 2
RANDOM_SEED = 1234
TIMEOUT = 240
VESSEL_NUM = 3


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
    scene, num_iterations, runtime = generate_scene(scenario, TIMEOUT, 0, )
    
    eval_data.evaluation_time = runtime.total_seconds()
    
    eval_data.best_fitness_index = np.inf
    eval_data.best_fitness = (np.inf)
    if scene is not None:
        builder = SceneBuilder()
        for obj in scene.objects:
            if obj.is_vessel:
                speed = np.linalg.norm(obj.velocity)
                valid_types = [t for t in ALL_VESSEL_TYPES if t.do_match(obj.length, speed)]
                vessel_type = PassengerShip() if obj.is_os else random.choice(valid_types)
                builder.set_state(ConcreteVessel(obj.id, obj.is_os, obj.length, obj.length*4, vessel_type.max_speed, vessel_type.name),
                                VesselState(obj.position[0], obj.position[1], speed, calculate_heading(obj.velocity[0], obj.velocity[1])))
        eval_data.best_scene = builder.build()
        eval_data.best_fitness_index = 0.0
        eval_data.best_fitness = (0.0)
    eval_data.number_of_generations = num_iterations
    
    eval_data.save_as_measurement()
    
    #ScenarioPlotManager(TrajectoryManager(builder.build()))
