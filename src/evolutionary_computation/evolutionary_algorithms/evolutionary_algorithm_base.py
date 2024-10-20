from copy import deepcopy
from datetime import datetime
import gc
import traceback
import os
import random
from typing import List, Tuple
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from abc import ABC, abstractmethod
from model.environment.functional_models.usv_env_desc_list import USV_ENV_DESC_LIST
from model.environment.usv_config import ASSET_FOLDER
from model.environment.usv_environment import USVEnvironment
from model.environment.usv_environment_desc import USVEnvironmentDesc


class EvolutionaryAlgorithmBase(ABC):
    def __init__(self, measurement_name: str, algorithm_desc : str, env_configs: List[str | USVEnvironmentDesc], test_config : EvaluationData,
                 number_of_runs : int, warmups : int, verbose : bool) -> None:
        self.measurement_name = measurement_name
        self.algorithm_desc = f'{algorithm_desc}_{test_config.aggregate_strat}'        
        
        self.env_configs : List[USVEnvironmentDesc] = []
        for config in env_configs:
            if isinstance(config, str):
                self.env_configs.append(USV_ENV_DESC_LIST[config])
            elif isinstance(config, USVEnvironmentDesc):
                self.env_configs.append(config)
            else:
                raise Exception('Unsupported env desc type.')
        self.test_config = test_config
        self.number_of_runs = number_of_runs
        self.warmups = warmups
        self.verbose = verbose
       
    def run(self) -> List[List[EvaluationData]]:
        self.set_seed(self.test_config.random_seed)
        
        for i in range(self.warmups):
            res = self.evaluate(self.env_configs[0], False)
        
        results : List[List[EvaluationData]] = []
        for config in self.env_configs:
            results.append([])
            for i in range(self.number_of_runs):
                res = self.evaluate(config, True)
                results[-1].append(res)
        return results
         
    def evaluate(self, config : USVEnvironmentDesc, save : bool) -> EvaluationData:
        try:
            eval_data = deepcopy(self.test_config)
            env = USVEnvironment(config, init_method=eval_data.init_method)
            eval_data.measurement_name = self.measurement_name
            eval_data.algorithm_desc = self.algorithm_desc
            eval_data.config_name = config.name
            eval_data.timestamp = datetime.now().isoformat()
            eval_data.config_group = config.group
            eval_data.vessel_number = config.vessel_num
            
            
            initial_pop = env.get_population(eval_data.population_size)            
            some_input = self.init_problem(env, initial_pop, eval_data)
            
            gc.collect()
            start_time = datetime.now()
            some_results = self.do_evaluate(some_input, eval_data)
            eval_data.evaluation_time = (datetime.now() - start_time).total_seconds()
            
            best_solution, best_fitness, number_of_generations = self.convert_results(some_results, eval_data)
            eval_data.best_solution = best_solution
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
                self.save_eval_data(eval_data)
            return eval_data
        
    @abstractmethod   
    def init_problem(self, env: USVEnvironment, initial_population : List[List[float]], eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def convert_results(self, some_results, eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        pass
    
    def save_eval_data(self, eval_data : EvaluationData):
        asset_folder = f'{ASSET_FOLDER}/gen_data/{eval_data.measurement_name}/{eval_data.config_group}/{eval_data.algorithm_desc}'
        if not os.path.exists(asset_folder):
            os.makedirs(asset_folder)
        file_path=f"{asset_folder}/{eval_data.config_name}_{eval_data.timestamp.replace(':','-')}.json"
        eval_data.path = file_path
        eval_data.save_to_json()
        
    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
    