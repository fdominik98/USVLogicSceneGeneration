from copy import deepcopy
from datetime import datetime
import gc
import traceback
import os
import random
from typing import List, Tuple, Union
import numpy as np
from logical_level.constraint_satisfaction.assignments import Assignments
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
from abc import ABC, abstractmethod
from logical_level.mapping.logical_scenario_builder import LogicalScenarioBuilder
from utils.file_system_utils import ASSET_FOLDER
from logical_level.models.logical_scenario import LogicalScenario
from functional_level.metamodels.functional_scenario import FunctionalScenario
from concrete_level.trajectory_generation.scene_builder import SceneBuilder
from utils.scenario import Scenario


class EvolutionaryAlgorithmBase(ABC):
    def __init__(self, measurement_name: str, algorithm_desc : str, scenarios: List[Scenario], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        self.measurement_name = measurement_name
        self.algorithm_desc = f'{algorithm_desc}_{test_config.aggregate_strat}'
        self.logical_scenarios = [LogicalScenarioBuilder.build(scenario, test_config.init_method) for scenario in scenarios]
        self.test_config = test_config
        self.number_of_runs = number_of_runs
        self.warmups = warmups
        self.verbose = verbose
       
    def run(self) -> List[List[EvaluationData]]:
        self.set_seed(self.test_config.random_seed)
        
        for i in range(self.warmups):
            res = self.evaluate(self.logical_scenarios[0], False)
        
        results : List[List[EvaluationData]] = []
        for scenario in self.logical_scenarios:
            results.append([])
            for i in range(self.number_of_runs):
                res = self.evaluate(scenario, True)
                results[-1].append(res)
        return results
         
    def evaluate(self, logical_scenario : LogicalScenario, save : bool) -> EvaluationData:
        try:
            eval_data = deepcopy(self.test_config)
            eval_data.vessel_number = logical_scenario.size
            eval_data.measurement_name = self.measurement_name
            eval_data.algorithm_desc = self.algorithm_desc
            eval_data.scenario_name = logical_scenario.name
            eval_data.timestamp = datetime.now().isoformat()            
            
            initial_pop = logical_scenario.get_population(eval_data.population_size)            
            some_input = self.init_problem(logical_scenario, initial_pop, eval_data)
            
            gc.collect()
            start_time = datetime.now()
            some_results = self.do_evaluate(some_input, eval_data)
            eval_data.evaluation_time = (datetime.now() - start_time).total_seconds()
            
            best_solution, best_fitness, number_of_generations = self.convert_results(some_results, eval_data)
            assignments = Assignments(logical_scenario.actor_vars).update_from_individual(best_solution)
            eval_data.best_scene = SceneBuilder().build_from_assignments(assignments)
            eval_data.best_fitness = best_fitness
            eval_data.number_of_generations = number_of_generations
            eval_data.best_fitness_index = sum(best_fitness)
            
            if self.verbose:
                print("Best individual is:", best_solution)
                print("Best individual fitness is:", best_fitness)
                
        except Exception as e:
            eval_data.error_message = f'{str(e)}\n{traceback.format_exc()}'
            print(eval_data.error_message)
        finally:
            if save:
                eval_data.save_as_measurement()
            return eval_data
        
    @abstractmethod   
    def init_problem(self, logical_scenario: LogicalScenario, initial_population : List[List[float]], eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def convert_results(self, some_results, eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        pass
        
    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
    