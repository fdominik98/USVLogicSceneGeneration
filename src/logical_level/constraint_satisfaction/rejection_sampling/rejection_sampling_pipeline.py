from typing import Any, List, Tuple
import numpy as np
from logical_level.constraint_satisfaction.aggregates import Aggregate
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.rejection_sampling.scenic_utils import calculate_solution, generate_scene, scenic_scenario
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.models.logical_scenario import LogicalScenario
from global_config import GlobalConfig, o2VisibilityByo1, possible_vis_distances
from utils.scenario import Scenario


class RejectionSamplingPipeline(SolverBase):
    algorithm_desc = 'scenic'
    
    def __init__(self, measurement_name: str, functional_scenarios: List[Scenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)
    
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
        default_population = initial_population[0]
        functional_scenario = self.scenarios[logical_scenario]
        assignments = Assignments(logical_scenario.actor_variables).update_from_individual(default_population)
        
        os_id = logical_scenario.os_variable.id
        ts_ids = [v.id for v in logical_scenario.ts_variables]
        obst_ids = [v.id for v in logical_scenario.obstacle_variables]
        length_map = {}
        radius_map = {}
        vis_distance_map = {}
        bearing_map = {}
        possible_distances_map = {}
        min_distance_map = {}
        
        for var in logical_scenario.actor_variables:
            length_map[var.id] = assignments[var].l
            radius_map[var.id] = assignments[var].r
            
        for ts_id in ts_ids:
            distances = possible_vis_distances(length_map[os_id], length_map[ts_id])
            possible_distances_map[(os_id, ts_id)] = distances
            min_distance_map[(os_id, ts_id)] = min(distances)
            
        for obst_id in obst_ids:
            vis_distance_map[(os_id, obst_id)] = o2VisibilityByo1(True, radius_map[obst_id])
            
        if functional_scenario is not None:
            os = functional_scenario.os_object
            for o in functional_scenario.ts_objects:
                vis_distance_map[(os.id, o.id)] = min(o2VisibilityByo1(functional_scenario.overtaking(os, o), length_map[o.id]),
                            o2VisibilityByo1(functional_scenario.overtaking(o, os), length_map[os.id]))
                
                sin_half_col_cone_theta = np.clip(max(radius_map[os.id], radius_map[o.id]) / vis_distance_map[(os.id, o.id)], -1, 1)
                angle_col_cone = abs(np.arcsin(sin_half_col_cone_theta)) * 2
                
                #heading_ego_to_ts, bearing_angle_ego_to_ts, heading_ts_to_ego, bearing_angle_ts_to_ego
                # heading_ego_to_ts: relative angle to ego heading
                # heading_ts_to_ego: relative angle to p12
                scenarios = [
                    (functional_scenario.head_on(os, o),                 (0.0,                               max(angle_col_cone, GlobalConfig.BOW_ANGLE), 0.0, max(angle_col_cone, GlobalConfig.BOW_ANGLE))),
                (functional_scenario.crossing_from_port(os, o),          (-GlobalConfig.BEAM_ROTATION_ANGLE, GlobalConfig.SIDE_ANGLE,                     -GlobalConfig.BEAM_ROTATION_ANGLE, GlobalConfig.SIDE_ANGLE)),
                    (functional_scenario.crossing_from_port(o, os),      (GlobalConfig.BEAM_ROTATION_ANGLE,  GlobalConfig.SIDE_ANGLE,                      GlobalConfig.BEAM_ROTATION_ANGLE, GlobalConfig.SIDE_ANGLE)),
                    (functional_scenario.overtaking_to_port(os, o),      (GlobalConfig.BEAM_ROTATION_ANGLE,  GlobalConfig.SIDE_ANGLE,                      -np.pi,   GlobalConfig.STERN_ANGLE)),
                    (functional_scenario.overtaking_to_port(o, os),      (-np.pi,                            GlobalConfig.STERN_ANGLE,  -GlobalConfig.BEAM_ROTATION_ANGLE,             GlobalConfig.SIDE_ANGLE)),
                    (functional_scenario.overtaking_to_starboard(os, o), (-GlobalConfig.BEAM_ROTATION_ANGLE, GlobalConfig.SIDE_ANGLE,           -np.pi,   GlobalConfig.STERN_ANGLE)),
                    (functional_scenario.overtaking_to_starboard(o, os), (-np.pi,                            GlobalConfig.STERN_ANGLE,  GlobalConfig.BEAM_ROTATION_ANGLE,  GlobalConfig.SIDE_ANGLE))
                ]
                
                for condition, bearing in scenarios:
                    if condition:
                        bearing_map[(os.id, o.id)] = bearing
                    
            for o in functional_scenario.obstacle_objects:
                os = functional_scenario.os_object
                
                sin_half_col_cone_theta = np.clip(max(radius_map[os.id], radius_map[o.id]) / vis_distance_map[(os.id, o.id)], -1, 1)
                angle_col_cone = abs(np.arcsin(sin_half_col_cone_theta)) * 2
                    
                if functional_scenario.dangerous_head_on_sector_of(o, os):
                    bearing_map[(os.id, o.id)] = (0.0, max(angle_col_cone, GlobalConfig.BOW_ANGLE), 0, 2*np.pi)
        
        scenario = scenic_scenario(os_id, ts_ids, obst_ids,
                                   length_map, radius_map, possible_distances_map, min_distance_map,
                                   vis_distance_map = vis_distance_map,
                                   bearing_map=bearing_map, verbose=self.verbose)
        
        aggregate = Aggregate.factory(logical_scenario, eval_data.aggregate_strat, minimize=True)
        return scenario, aggregate, default_population
    
    def do_evaluate(self, some_input : Tuple[Any, LogicalScenario, List[float]], eval_data : EvaluationData):
        scenario, aggregate, default_population = some_input
        scene, num_iterations, runtime, empty_region = generate_scene(scenario, eval_data.timeout, aggregate, np.inf if self.verbose else 0)
        return scene, num_iterations, default_population       
    
    def convert_results(self, some_results : Tuple[Any, int, List[float]], eval_data : EvaluationData) -> Tuple[List[float], int]:
        scene, num_iterations, default_population = some_results
        if scene is None:
            return default_population, num_iterations
        return calculate_solution(scene), num_iterations