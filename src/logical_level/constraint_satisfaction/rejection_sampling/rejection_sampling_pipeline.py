from itertools import chain
from typing import Any, List, Tuple

import numpy as np
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.constraint_satisfaction.aggregates import Aggregate
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.rejection_sampling.scenic_utils import generate_scene, scenic_scenario
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.models.logical_model_manager import LogicalModelManager
from logical_level.models.logical_scenario import LogicalScenario
from logical_level.models.relation_constraints import CrossingBear
from utils.asv_utils import BEAM_ANGLE, BOW_ANGLE, MASTHEAD_LIGHT_ANGLE, N_MILE_TO_M_CONVERSION, STERN_ANGLE, o2VisibilityByo1, calculate_heading


class RejectionSamplingPipeline(SolverBase):
    def __init__(self, measurement_name: str, functional_scenarios: List[FunctionalScenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'scenic_rejection_sampling', functional_scenarios, test_config, number_of_runs, warmups, verbose)
        self.scenario_map = {logical_scenario : functional_scenarios[i] for i, logical_scenario in enumerate(self.logical_scenarios)}
    
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
        initial_population = initial_population[0]
        functional_scenario = self.scenario_map[logical_scenario]
        object_map = {obj : var for var, obj in zip(logical_scenario.actor_vars, functional_scenario.func_objects)}
        assignments = Assignments(logical_scenario.actor_vars).update_from_individual(initial_population)
        
        length_map = {}
        vis_distance_map = {}
        bearing_map = {}
        
        for os, ts in functional_scenario.os_ts_pairs:
            length_map[os.id] = assignments[object_map[os]].l
            length_map[ts.id] = assignments[object_map[ts]].l
            vis_distance_map[(os.id, ts.id)] = min(o2VisibilityByo1(functional_scenario.overtaking(os, ts), length_map[ts.id]),
                           o2VisibilityByo1(functional_scenario.overtaking(ts, os), length_map[os.id])) *  N_MILE_TO_M_CONVERSION
            
            #heading_ego_to_ts, bearing_angle_ego_to_ts, heading_ts_to_ego, bearing_angle_ts_to_ego
            # heading_ego_to_ts: relative angle to ego heading
            # heading_ts_to_ego: relative angle to p12
            if functional_scenario.head_on(os, ts):
                bearing_map[(os.id, ts.id)] = (0.0, BOW_ANGLE, 0.0, BOW_ANGLE)
            if functional_scenario.crossing(os, ts):
                bearing_map[(os.id, ts.id)] = (0.0, MASTHEAD_LIGHT_ANGLE, -CrossingBear.rotation_angle, BEAM_ANGLE)
            if functional_scenario.crossing(ts, os):
                bearing_map[(os.id, ts.id)] = (CrossingBear.rotation_angle, BEAM_ANGLE, 0, MASTHEAD_LIGHT_ANGLE)
            if functional_scenario.overtaking(os, ts):
                bearing_map[(os.id, ts.id)] = (0.0, MASTHEAD_LIGHT_ANGLE, -np.pi, MASTHEAD_LIGHT_ANGLE)
            if functional_scenario.overtaking(ts, os):
                bearing_map[(os.id, ts.id)] = (-np.pi, STERN_ANGLE, 0, MASTHEAD_LIGHT_ANGLE)
            
        scenario = scenic_scenario(eval_data.vessel_number, vis_distance_map = vis_distance_map, length_map = length_map, bearing_map=bearing_map)
        
        return scenario, logical_scenario, initial_population
    
    def do_evaluate(self, some_input : Tuple[Any, LogicalScenario, List[float]], eval_data : EvaluationData):
        scenario, logicalScenario, initial_population = some_input
        scene, num_iterations, runtime = generate_scene(scenario, eval_data.timeout, 0)
        return scene, num_iterations, logicalScenario, initial_population       
    
    def convert_results(self, some_results : Tuple[Any, int, LogicalScenario, List[float]], eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        scene, num_iterations, logicalScenario, initial_population = some_results
        if scene is None:
            solution = initial_population
        else:            
            objects = sorted([obj for obj in scene.objects if obj.is_vessel], key=lambda obj: obj.id)
            solution = list(chain.from_iterable([[obj.position[0], obj.position[1],
                                                    calculate_heading(obj.velocity[0], obj.velocity[1]), obj.length, np.linalg.norm(obj.velocity)] for obj in objects]))
        penalty = Aggregate.factory(logicalScenario, eval_data.aggregate_strat, minimize=True).derive_penalty(solution)
        print(penalty.info)
        return solution, [penalty.total_penalty], num_iterations