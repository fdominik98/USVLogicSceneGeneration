from typing import Any, List, Tuple
import numpy as np
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.rejection_sampling.scenic_utils import calculate_solution, generate_scene, scenic_scenario
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.models.logical_scenario import LogicalScenario
from utils.asv_utils import BEAM_ANGLE, BEAM_ROTATION_ANGLE, BOW_ANGLE, MASTHEAD_LIGHT_ANGLE, STERN_ANGLE, o2VisibilityByo1, vessel_radius
from utils.scenario import Scenario


class RejectionSamplingPipeline(SolverBase):
    algorithm_desc = 'scenic'
    
    def __init__(self, measurement_name: str, functional_scenarios: List[Scenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)
    
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
        population = initial_population[0]
        functional_scenario = self.scenarios[logical_scenario]
        assignments = Assignments(logical_scenario.actor_variables).update_from_individual(population)
        
        os_id = logical_scenario.os_variable.id
        ts_ids = [v.id for v in logical_scenario.ts_variables]
        obst_ids = [v.id for v in logical_scenario.obstacle_variables]
        length_map = {}
        radius_map = {}
        vis_distance_map = {}
        bearing_map = {}
        
        for var in logical_scenario.actor_variables:
            length_map[var.id] = assignments[var].l
            radius_map[var.id] = assignments[var].r
        
        if functional_scenario is not None:
            os = functional_scenario.os_object
            for o in functional_scenario.ts_objects:
                vis_distance_map[(os.id, o.id)] = min(o2VisibilityByo1(functional_scenario.overtaking(os, o), length_map[o.id]),
                            o2VisibilityByo1(functional_scenario.overtaking(o, os), length_map[os.id]))
                
                sin_half_cone_p12_theta = np.clip(vessel_radius(length_map[o.id]) / vis_distance_map[(os.id, o.id)], -1, 1)
                angle_half_cone_p12 = abs(np.arcsin(sin_half_cone_p12_theta))
                sin_half_cone_p21_theta = np.clip(vessel_radius(length_map[os.id]) / vis_distance_map[(os.id, o.id)], -1, 1)
                angle_half_cone_p21 = abs(np.arcsin(sin_half_cone_p21_theta))
                
                #heading_ego_to_ts, bearing_angle_ego_to_ts, heading_ts_to_ego, bearing_angle_ts_to_ego
                # heading_ego_to_ts: relative angle to ego heading
                # heading_ts_to_ego: relative angle to p12
                if functional_scenario.head_on(os, o):
                    bearing_map[(os.id, o.id)] = (0.0, max(angle_half_cone_p12, BOW_ANGLE), 0.0, max(angle_half_cone_p21, BOW_ANGLE))
                if functional_scenario.crossing_from_port(os, o):
                    bearing_map[(os.id, o.id)] = (-BEAM_ROTATION_ANGLE, BEAM_ANGLE, -BEAM_ROTATION_ANGLE, BEAM_ANGLE)
                if functional_scenario.crossing_from_port(o, os):
                    bearing_map[(os.id, o.id)] = (BEAM_ROTATION_ANGLE, BEAM_ANGLE, BEAM_ROTATION_ANGLE, BEAM_ANGLE)
                if functional_scenario.overtaking_to_port(os, o):
                    bearing_map[(os.id, o.id)] = (BEAM_ROTATION_ANGLE, BEAM_ANGLE, -np.pi, STERN_ANGLE)
                if functional_scenario.overtaking_to_port(o, os):
                    bearing_map[(os.id, o.id)] = (-np.pi, STERN_ANGLE, -BEAM_ROTATION_ANGLE, BEAM_ANGLE)
                if functional_scenario.overtaking_to_starboard(os, o):
                    bearing_map[(os.id, o.id)] = (-BEAM_ROTATION_ANGLE, BEAM_ANGLE, -np.pi, STERN_ANGLE)
                if functional_scenario.overtaking_to_starboard(o, os):
                    bearing_map[(os.id, o.id)] = (-np.pi, STERN_ANGLE, BEAM_ROTATION_ANGLE, BEAM_ANGLE)
                    
            for o in functional_scenario.obstacle_objects:
                os = functional_scenario.os_object
                vis_distance_map[(os.id, o.id)] = o2VisibilityByo1(True, radius_map[o.id])
                
                sin_half_cone_p12_theta = np.clip(vessel_radius(length_map[o.id]) / vis_distance_map[(os.id, o.id)], -1, 1)
                angle_half_cone_p12 = abs(np.arcsin(sin_half_cone_p12_theta))
                    
                if functional_scenario.dangerous_head_on_sector_of(o, os):
                    bearing_map[(os.id, o.id)] = (0.0, max(angle_half_cone_p12, BOW_ANGLE), 0, 2*np.pi)
        
        scenario = scenic_scenario(os_id, ts_ids, obst_ids,
                                   length_map, radius_map, vis_distance_map = vis_distance_map,
                                   bearing_map=bearing_map, verbose=self.verbose)
        
        return scenario, logical_scenario, population
    
    def do_evaluate(self, some_input : Tuple[Any, LogicalScenario, List[float]], eval_data : EvaluationData):
        scenario, logicalScenario, population = some_input
        scene, num_iterations, runtime, empty_region = generate_scene(scenario, eval_data.timeout, np.inf if self.verbose else 0)
        return scene, num_iterations, logicalScenario, population       
    
    def convert_results(self, some_results : Tuple[Any, int, LogicalScenario, List[float]], eval_data : EvaluationData) -> Tuple[List[float], int]:
        scene, num_iterations, logicalScenario, population = some_results
        solution = calculate_solution(population, scene)
        return solution, num_iterations