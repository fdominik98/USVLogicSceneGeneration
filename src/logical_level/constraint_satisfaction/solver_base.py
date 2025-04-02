from copy import deepcopy
from datetime import datetime
import gc
import os
import traceback
import random
from typing import Dict, List, Optional, Tuple
import numpy as np
import psutil
from functional_level.metamodels.functional_scenario import FunctionalScenario
from logical_level.constraint_satisfaction.aggregates import Aggregate
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evaluation_data import EvaluationData
from abc import ABC, abstractmethod
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from logical_level.models.logical_scenario import LogicalScenario
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from utils.scenario import Scenario
from itertools import cycle, islice


class SolverBase(ABC):
    algorithm_desc = 'unspecified'
    
    def __init__(self, measurement_name: str, scenarios: List[Scenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        self.measurement_name = measurement_name
        self.scenarios : Dict[LogicalScenario, Optional[FunctionalScenario]] = dict([LogicalScenarioBuilder.build(scenario, test_config.init_method) for scenario in scenarios])
        self.test_config = test_config
        self.number_of_runs = number_of_runs
        self.warmups = warmups
        self.verbose = verbose
       
    def run(self, core_id : int):
        self.set_seed(self.test_config.random_seed)
        
        for logical_scenario in islice(cycle(self.scenarios.keys()), self.warmups):
            self.__evaluate(logical_scenario, core_id, False)
        
        for logical_scenario in islice(cycle(self.scenarios.keys()), self.number_of_runs):
            self.__evaluate(logical_scenario, core_id, True)
         
    def __evaluate(self, logical_scenario : LogicalScenario, core_id : int,  save : bool):
        try:
            eval_data = deepcopy(self.test_config)
            eval_data.vessel_number = logical_scenario.vessel_number
            eval_data.obstacle_number = logical_scenario.obstacle_number
            eval_data.measurement_name = self.measurement_name
            eval_data.algorithm_desc = self.algorithm_desc
            eval_data.scenario_name = logical_scenario.name
            eval_data.timestamp = datetime.now().isoformat()            
            
            initial_pop = logical_scenario.get_population(eval_data.population_size)            
            some_input = self.init_problem(logical_scenario, initial_pop, eval_data)
            
            gc.collect()
            p = psutil.Process(os.getpid()) # Ensure dedicated cpu
            p.cpu_affinity([core_id])
            
            start_time = datetime.now()
            some_results = self.do_evaluate(some_input, eval_data)
            eval_data.evaluation_time = (datetime.now() - start_time).total_seconds()
            
            best_solution, number_of_generations = self.convert_results(some_results, eval_data)
            assignments = Assignments(logical_scenario.actor_variables).update_from_individual(best_solution)
            eval_data.best_scene = SceneBuilder().build_from_assignments(assignments)
            eval_data.number_of_generations = number_of_generations
            
            aggregate = Aggregate.factory(logical_scenario, eval_data.aggregate_strat, minimize=True)
            penalty = aggregate.derive_penalty(best_solution)
            eval_data.best_fitness = aggregate.evaluate(best_solution)
            eval_data.best_fitness_index = penalty.total_penalty
            
            if self.verbose:
                print(penalty.pretty_info())            
                print("Best individual is:", best_solution)
                print("Best individual fitness is:", eval_data.best_fitness)
                
            if round(eval_data.evaluation_time) < eval_data.timeout and not penalty.is_zero:
                raise ValueError('Something went wrong.')
                
        except Exception as e:
            eval_data.error_message = f'{str(e)}\n{traceback.format_exc()}'
            print(eval_data.error_message)
        finally:
            if save:
                eval_data.save_as_measurement()
        
    @abstractmethod   
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def convert_results(self, some_results, eval_data : EvaluationData) -> Tuple[List[float], int]:
        pass
        
    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
        
    