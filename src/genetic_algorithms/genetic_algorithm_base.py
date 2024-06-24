import random
from typing import Optional

import numpy as np
from aggregates import Aggregate
from genetic_algorithms.evaluation_data import EvaluationData
from model.colreg_situation import CrossingFromPort, HeadOn, NoColision, NoConstraint, Overtake
from model.colreg_situation_config import ColregSituationConfig
from model.usv_environment import USVEnvironment
from model.usv_environment_config import USVEnvironmentConfig
from abc import ABC, abstractmethod
from datetime import datetime
import gc
import traceback
import os
from model.usv_config import *
from src.visualization.colreg_plot import ColregPlot

class GeneticAlgorithmBase(ABC):
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    usv_environment_configs : dict[str, USVEnvironmentConfig] = {
        'overtaking_and_crossing' : USVEnvironmentConfig('overtaking_and_crossing', [50.0, 50.0, 50.0],
                                                                                  [ColregSituationConfig(0, CrossingFromPort, 1, [1800, 1900]),
                                                                                   ColregSituationConfig(2, Overtake, 0, [1800, 1900]),
                                                                                   ColregSituationConfig(2, NoColision, 1, [1800, max_distance])]),
        
        'two_way_crossing' : USVEnvironmentConfig('two_way_crossing', [50.0, 50.0, 50.0],
                                                                                  [ColregSituationConfig(0, CrossingFromPort, 1, [1800, 1900]),
                                                                                   ColregSituationConfig(2, CrossingFromPort, 0, [1800, 1900]),
                                                                                   ColregSituationConfig(1, NoColision, 2, [1800, max_distance])]),
        
        'crossing_and_head_on' : USVEnvironmentConfig('crossing_and_head_on', [50.0, 50.0, 50.0],
                                                                                  [ColregSituationConfig(0, HeadOn, 1, [1800, 1900]),                                                                                   ColregSituationConfig(0, NoColision, 2, None),
                                                                                   ColregSituationConfig(2, CrossingFromPort, 0, [1800, 1900]),
                                                                                   ColregSituationConfig(1, NoColision, 2, [1800, max_distance])]),
        
        'overtaking_and_head_on' : USVEnvironmentConfig('overtaking_and_head_on', [50.0, 50.0, 50.0],
                                                                                  [ColregSituationConfig(0, HeadOn, 1, [1800, 1900]),                                                                                   ColregSituationConfig(0, NoColision, 2, None),
                                                                                   ColregSituationConfig(2, Overtake, 0, [1800, 1900]),
                                                                                   ColregSituationConfig(1, NoColision, 2, [1800, max_distance])]),
        
        'two_way_overtaking' : USVEnvironmentConfig('two_way_overtaking', [50.0, 50.0, 50.0],
                                                                                  [ColregSituationConfig(0, Overtake, 1, [1800, 1900]),                                                                                   ColregSituationConfig(0, NoColision, 2, None),
                                                                                   ColregSituationConfig(2, Overtake, 0, [1800, 1900]),
                                                                                   ColregSituationConfig(1, NoColision, 2, [1800, max_distance])]),
        
        'two_way_overtaking_and_crossing' : USVEnvironmentConfig('two_way_overtaking_and_crossing', [50.0, 50.0, 50.0, 50.0],
                                                                                  [ColregSituationConfig(0, Overtake, 1, [1800, 1900]),                                                                                   ColregSituationConfig(0, NoColision, 2, None),
                                                                                   ColregSituationConfig(2, Overtake, 0, [1800, 1900]),
                                                                                   ColregSituationConfig(1, NoColision, 2, [1800, max_distance]),
                                                                                   ColregSituationConfig(3, CrossingFromPort, 0, [1800, 1900]),                                                                                   ColregSituationConfig(0, NoColision, 2, None),
                                                                                   ColregSituationConfig(3, NoColision, 1, [1800, max_distance]),
                                                                                   ColregSituationConfig(3, NoColision, 2, [1800, max_distance])]),
    }
    
    def __init__(self, measurement_name: str, algorithm_desc : str, config_name : str, verbose : bool) -> None:
        self.measurement_name = f'{measurement_name} - {datetime.now().isoformat().replace(':','-')}'
        self.algorithm_desc = algorithm_desc
        self.config_name = config_name
        self.env_config = self.usv_environment_configs[config_name]
        self.env = USVEnvironment(self.env_config)
        self.aggregate = self.get_aggregate(self.env)
        self.verbose = verbose
        self.initial_population_array = self.env.get_population(200)
            
        
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
                                    timestamp=timestamp)
            
            random.seed(random_seed)
            np.random.seed(random_seed)
            
            some_input = self.init_problem(self.initial_population_array[:population_size], eval_data)
            gc.collect()
            start_time = datetime.now()
            some_results = self.do_evaluate(some_input, eval_data)
            eval_data.evaluation_time = (datetime.now() - start_time).total_seconds()
            
            best_solution, best_fitness = self.convert_results(some_results, eval_data)
            eval_data.best_solution = best_solution
            eval_data.best_fitness = best_fitness
            if self.verbose:
                print("Best individual is:", best_solution)
                print("Best individual fitness is:", best_fitness)
                ColregPlot(self.env.update(best_solution))
        except Exception as e:
            eval_data.error_message = f'{str(e)}\n{traceback.format_exc()}'
            print(eval_data.error_message)
        finally:
            self.save_eval_data(eval_data)
            return eval_data
        
    @abstractmethod   
    def init_problem(self, initial_population : list[list[float]], eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def do_evaluate(self, some_input, eval_data : EvaluationData):
        pass
    
    @abstractmethod   
    def convert_results(self, some_results, eval_data : EvaluationData) -> tuple[list[float], list[float]]:
        pass
    
    def save_eval_data(self, eval_data : EvaluationData):
        asset_folder = f'{self.current_file_directory}/../../assets/{self.algorithm_desc}/{self.config_name}/{self.measurement_name}'
        if not os.path.exists(asset_folder):
            os.makedirs(asset_folder)
        
        eval_data.save_to_json(file_path=f'{asset_folder}/{eval_data.timestamp.replace(':','-')}.json')
    