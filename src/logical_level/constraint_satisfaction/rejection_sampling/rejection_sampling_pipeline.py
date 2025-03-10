from typing import Any, List, Tuple
import numpy as np
from logical_level.constraint_satisfaction.aggregates import Aggregate
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.rejection_sampling.scenic_utils import calculate_solution, generate_scene, scenic_scenario
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.models.logical_scenario import LogicalScenario
from logical_level.models.relation_constraints import CrossingBear
from utils.asv_utils import BEAM_ANGLE, BOW_ANGLE, MASTHEAD_LIGHT_ANGLE, STERN_ANGLE, o2VisibilityByo1, vessel_radius
from utils.scenario import Scenario


class RejectionSamplingPipeline(SolverBase):
    algorithm_desc = 'scenic'
    
    def __init__(self, measurement_name: str, functional_scenarios: List[Scenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, functional_scenarios, test_config, number_of_runs, warmups, verbose)
    
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
        population = initial_population[0]
        functional_scenario = self.scenarios[logical_scenario]
        assignments = Assignments(logical_scenario.actor_vars).update_from_individual(population)
        
        length_map = {}
        vis_distance_map = {}
        bearing_map = {}
        
        for var in logical_scenario.actor_vars:
            length_map[var.id] = assignments[var].l
        
        if functional_scenario is not None:
            for os, ts in functional_scenario.os_ts_pairs:
                vis_distance_map[(os.id, ts.id)] = min(o2VisibilityByo1(functional_scenario.overtaking(os, ts), length_map[ts.id]),
                            o2VisibilityByo1(functional_scenario.overtaking(ts, os), length_map[os.id]))
                
                sin_half_cone_p12_theta = np.clip(vessel_radius(length_map[ts.id]) / vis_distance_map[(os.id, ts.id)], -1, 1)
                angle_half_cone_p12 = abs(np.arcsin(sin_half_cone_p12_theta))
                sin_half_cone_p21_theta = np.clip(vessel_radius(length_map[os.id]) / vis_distance_map[(os.id, ts.id)], -1, 1)
                angle_half_cone_p21 = abs(np.arcsin(sin_half_cone_p21_theta))
                
                #heading_ego_to_ts, bearing_angle_ego_to_ts, heading_ts_to_ego, bearing_angle_ts_to_ego
                # heading_ego_to_ts: relative angle to ego heading
                # heading_ts_to_ego: relative angle to p12
                if functional_scenario.head_on(os, ts):
                    bearing_map[(os.id, ts.id)] = (0.0, max(angle_half_cone_p12, BOW_ANGLE), 0.0, max(angle_half_cone_p21, BOW_ANGLE))
                if functional_scenario.crossing(os, ts):
                    bearing_map[(os.id, ts.id)] = (-CrossingBear.rotation_angle, BEAM_ANGLE, -CrossingBear.rotation_angle, BEAM_ANGLE)
                if functional_scenario.crossing(ts, os):
                    bearing_map[(os.id, ts.id)] = (CrossingBear.rotation_angle, BEAM_ANGLE, CrossingBear.rotation_angle, BEAM_ANGLE)
                if functional_scenario.overtaking(os, ts):
                    bearing_map[(os.id, ts.id)] = (0.0, MASTHEAD_LIGHT_ANGLE, -np.pi, STERN_ANGLE)
                if functional_scenario.overtaking(ts, os):
                    bearing_map[(os.id, ts.id)] = (-np.pi, STERN_ANGLE, 0, MASTHEAD_LIGHT_ANGLE)
            
        scenario = scenic_scenario(eval_data.vessel_number, length_map, vis_distance_map = vis_distance_map, bearing_map=bearing_map)
        
        return scenario, logical_scenario, population
    
    def do_evaluate(self, some_input : Tuple[Any, LogicalScenario, List[float]], eval_data : EvaluationData):
        scenario, logicalScenario, population = some_input
        scene, num_iterations, runtime, empty_region = generate_scene(scenario, eval_data.timeout, np.inf if self.verbose else 0)
        return scene, num_iterations, logicalScenario, population       
    
    def convert_results(self, some_results : Tuple[Any, int, LogicalScenario, List[float]], eval_data : EvaluationData) -> Tuple[List[float], int]:
        scene, num_iterations, logicalScenario, population = some_results
        solution = calculate_solution(population, scene)
        return solution, num_iterations