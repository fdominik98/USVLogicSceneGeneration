from copy import deepcopy
from datetime import datetime
import gc
import os
import traceback
import random
from typing import List, Tuple
import numpy as np
import psutil
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.constraint_satisfaction.aggregates import Aggregate
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from logical_level.constraint_satisfaction.general_constraint_satisfaction import Solver
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from logical_level.models.logical_scenario import LogicalScenario
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from itertools import cycle, islice

class MSRConstraintSatisfaction():
    def __init__(self, solver : Solver, measurement_name: str, functional_scenarios: List[FunctionalScenario],
                 test_config : EvaluationData, warmups : int, average_time_per_scene : int, verbose: bool) -> None:
        self.solver = solver
        self.measurement_name = measurement_name
        self.scenarios : List[Tuple[LogicalScenario, FunctionalScenario]] = [(LogicalScenarioBuilder.build_from_functional(scenario, test_config.init_method),
                                                                                      scenario) for scenario in functional_scenarios]
        self.test_config = test_config
        self.warmups = warmups
        self.verbose = verbose
        self.max_eval_time = average_time_per_scene * len(self.scenarios)
        self.set_seed(self.test_config.random_seed)
        
       
    def run(self, core_id : int):
        for logical_scenario, functional_scenario in islice(cycle(self.scenarios), self.warmups):
            self.__evaluate(logical_scenario, functional_scenario, core_id, False, 0)
        
        coverage = {logical_scenario : False for logical_scenario, _ in self.scenarios}
        eval_time = 0
        for logical_scenario, functional_scenario in cycle(self.scenarios):
            remaining = list(coverage.values()).count(False)
            if remaining == 0 or eval_time >= self.max_eval_time:
                break
            
            if coverage[logical_scenario]:
                continue
            
            print(f"Covered scenarios: {len(self.scenarios) - remaining}/{len(self.scenarios)}")
            eval_data = self.__evaluate(logical_scenario, functional_scenario, core_id, True, eval_time)
            eval_time += eval_data.evaluation_time
            coverage[logical_scenario] = eval_data.is_valid
                
         
    def __evaluate(self, logical_scenario : LogicalScenario, functional_scenario : FunctionalScenario,
                   core_id : int,  save : bool, current_eval_time : float) -> EvaluationData:
        try:
            eval_data = deepcopy(self.test_config)
            eval_data.vessel_number = logical_scenario.vessel_number
            eval_data.obstacle_number = logical_scenario.obstacle_number
            eval_data.measurement_name = self.measurement_name
            eval_data.algorithm_desc = self.solver.algorithm_desc()
            eval_data.scenario_name = logical_scenario.name
            eval_data.timestamp = datetime.now().isoformat()            
            
            initial_pop = logical_scenario.get_population(eval_data.population_size)            
            some_input = self.solver.init_problem(logical_scenario, functional_scenario, initial_pop, eval_data)
            
            gc.collect()
            p = psutil.Process(os.getpid()) # Ensure dedicated cpu
            p.cpu_affinity([core_id])
            
            start_time = datetime.now()
            some_results = self.solver.do_evaluate(some_input, eval_data)
            eval_data.evaluation_time = (datetime.now() - start_time).total_seconds()
            
            best_solution, number_of_generations = self.solver.convert_results(some_results, eval_data)
            assignments = Assignments(logical_scenario.actor_variables).update_from_individual(best_solution)
            eval_data.best_scene = SceneBuilder().build_from_assignments(assignments)
            eval_data.number_of_generations = number_of_generations
            
            aggregate = Aggregate.factory(logical_scenario, eval_data.aggregate_strat, minimize=True)
            penalty = aggregate.derive_penalty(best_solution)
            eval_data.best_fitness = aggregate.evaluate(best_solution)
            eval_data.best_fitness_index = penalty.value
            
            if self.verbose:
                print(penalty.pretty_info())            
                print("Best individual is:", best_solution)
                print("Best individual fitness is:", eval_data.best_fitness)
                
            if round(eval_data.evaluation_time) + 1 < eval_data.timeout and not penalty.is_zero:
                raise ValueError('Something went wrong.')
                
        except Exception as e:
            eval_data.error_message = f'{str(e)}\n{traceback.format_exc()}'
            print(eval_data.error_message)
        finally:
            if save and (current_eval_time + eval_data.evaluation_time) <= self.max_eval_time + 10:
                eval_data.save_as_measurement()
            return eval_data

        
    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
        
    