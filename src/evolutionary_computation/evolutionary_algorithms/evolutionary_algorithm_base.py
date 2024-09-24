from datetime import datetime
import gc
import traceback
import os
import sys
import random
from typing import List, Optional, Tuple
import numpy as np
from evolutionary_computation.aggregates import Aggregate
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.usv_environment import USVEnvironment
from abc import ABC, abstractmethod
from model.environment.usv_env_desc_list import USV_ENV_DESC_LIST
from model.environment.usv_config import ASSET_FOLDER


class GeneticAlgorithmBase(ABC):
    def __init__(self, measurement_name: str, algorithm_desc : str, config_name : str, verbose : bool, random_init : bool = True, runtime : int = 300) -> None:
        self.measurement_id = f"{measurement_name} - {datetime.now().isoformat().replace(':','-')}"
        self.measurement_name = measurement_name
        self.algorithm_desc = algorithm_desc
        self.config_name = config_name
        self.env_config = USV_ENV_DESC_LIST[config_name]
        self.env = USVEnvironment(self.env_config, random_init=random_init)
        self.aggregate = self.get_aggregate(self.env)
        self.verbose = verbose
        self.current_seed = None
        self.runtime = runtime
        
    @abstractmethod
    def get_aggregate(self, env) -> Aggregate:
        pass
    
    def evaluate(self, number_of_generations: int,
                 random_seed: int,
                 population_size: Optional[int],
                 num_parents_mating: Optional[int],
                 mutate_eta : Optional[float],
                 mutate_prob : Optional[float],
                 crossover_eta : Optional[float],
                 crossover_prob : Optional[float]) -> EvaluationData:
        
        try:
            timestamp = datetime.now().isoformat()
            eval_data = EvaluationData(algorithm_desc = self.algorithm_desc, config_name = self.config_name, random_seed = random_seed, 
                                    number_of_generations = number_of_generations, population_size = population_size, num_parents_mating = num_parents_mating,
                                    mutate_eta = mutate_eta, mutate_prob = mutate_prob, crossover_eta=crossover_eta, crossover_prob=crossover_prob,
                                    timestamp=timestamp, measurement_name=self.measurement_name)
            
            self.set_seed(random_seed)
            eval_data.number_of_generations = number_of_generations if number_of_generations is not None else sys.maxsize
            
            initial_pop = self.env.get_population(population_size)
            
            some_input = self.init_problem(initial_pop, eval_data)
            gc.collect()
            start_time = datetime.now()
            some_results = self.do_evaluate(some_input, eval_data)
            eval_data.evaluation_time = (datetime.now() - start_time).total_seconds()
            
            best_solution, best_fitness, number_of_generations = self.convert_results(some_results, eval_data)
            eval_data.best_solution = best_solution
            eval_data.best_fitness = best_fitness
            eval_data.actual_number_of_generations = number_of_generations
            
            if self.verbose:
                print("Best individual is:", best_solution)
                print("Best individual fitness is:", best_fitness)
                
        except Exception as e:
            eval_data.error_message = f'{str(e)}\n{traceback.format_exc()}'
            print(eval_data.error_message)
        finally:
            self.save_eval_data(eval_data)
            return eval_data
        
    @abstractmethod   
    def init_problem(self, initial_population : List[List[float]], eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def convert_results(self, some_results, eval_data : EvaluationData) -> Tuple[List[float], List[float], int]:
        pass
    
    def save_eval_data(self, eval_data : EvaluationData):
        asset_folder = f'{ASSET_FOLDER}/gen_data/{self.algorithm_desc}/{self.config_name}/{self.measurement_id}'
        if not os.path.exists(asset_folder):
            os.makedirs(asset_folder)
        file_path=f"{asset_folder}/{eval_data.timestamp.replace(':','-')}.json"
        eval_data.path = file_path
        eval_data.save_to_json(file_path=file_path)
        
    def set_seed(self, seed):
        if self.current_seed == seed:
            return
        random.seed(seed)
        np.random.seed(seed)
        self.current_seed = seed
    