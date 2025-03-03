from itertools import chain
from typing import Any, List, Tuple

import numpy as np
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.constraint_satisfaction.aggregates import Aggregate
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.rejection_sampling.scenic_sampling import calculate_heading, generate_scene, scenic_scenario
from logical_level.constraint_satisfaction.solver_base import SolverBase
from logical_level.models.logical_scenario import LogicalScenario
from utils.asv_utils import N_MILE_TO_M_CONVERSION, o2VisibilityByo1


class RejectionSamplingPipeline(SolverBase):
    def __init__(self, measurement_name: str, functional_scenarios: List[FunctionalScenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        super().__init__(measurement_name, 'scenic_rejection_sampling', functional_scenarios, test_config, number_of_runs, warmups, verbose)
        self.scenario_map = {logical_scenario : functional_scenarios[i] for i, logical_scenario in enumerate(self.logical_scenarios)}
    
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
        functional_scenario = self.scenario_map[logical_scenario]
        object_map = {obj : var for var, obj in zip(logical_scenario.actor_vars, functional_scenario.func_objects)}
        assignments = Assignments(logical_scenario.actor_vars).update_from_individual(initial_population[0])
        
        length_map = {}
        vis_distance_map = {}
        
        for os, ts in functional_scenario.os_ts_pairs:
            length_map[os.id] = assignments[object_map[os]].l
            length_map[ts.id] = assignments[object_map[ts]].l
            vis_distance_map[(os.id, ts.id)] = min(o2VisibilityByo1(functional_scenario.overtaking(os, ts), length_map[ts.id]),
                           o2VisibilityByo1(functional_scenario.overtaking(ts, os), length_map[os.id])) *  N_MILE_TO_M_CONVERSION
            
        scenario = scenic_scenario(eval_data.vessel_number, vis_distance_map = vis_distance_map, length_map = length_map)
        
        return scenario, logical_scenario
    
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        scenario, logicalScenario = some_input
        scene, num_iterations, runtime = generate_scene(scenario, eval_data.timeout, 0)
        return scene, num_iterations, logicalScenario
       
    
    def convert_results(self, some_results : Tuple[Any, int, LogicalScenario], eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        scene, num_iterations, logicalScenario = some_results
        objects = sorted([obj for obj in scene.objects if obj.is_vessel], key=lambda obj: obj.id)
        solution = list(chain.from_iterable([[obj.position[0], obj.position[1],
                                                   calculate_heading(obj.velocity[0], obj.velocity[1]), obj.length, np.linalg.norm(obj.velocity)] for obj in objects]))
        best_fitness = Aggregate.factory(logicalScenario, eval_data.aggregate_strat, minimize=True).evaluate(solution)
        return solution, best_fitness, num_iterations