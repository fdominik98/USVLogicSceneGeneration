from dataclasses import dataclass
import json
import os
import pprint
from typing import Optional, List
from concrete_level.models.concrete_scene import ConcreteScene
from utils.file_system_utils import ASSET_FOLDER
from utils.serializable import Serializable

@dataclass(frozen=False)
class EvaluationData(Serializable):
    algorithm_desc: Optional[str] = None
    scenario_name: Optional[str] = None
    random_seed: Optional[int] = None
    vessel_number: Optional[int] = None
    evaluation_time: Optional[float] = None
    number_of_generations: Optional[int] = None
    population_size: Optional[int] = None
    num_parents_mating: Optional[int] = None
    best_fitness: Optional[List[float]] = None
    mutate_eta: Optional[float] = None
    mutate_prob: Optional[float] = None
    crossover_eta: Optional[float] = None
    crossover_prob: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: Optional[str] = None
    measurement_name: Optional[str] = None
    path: Optional[str] = None
    timeout: Optional[float] = None
    init_method: Optional[str] = None
    c_1: Optional[float] = None  # cognitive coefficient
    c_2: Optional[float] = None  # social coefficient
    w: Optional[float] = None    # inertia weight
    best_fitness_index: Optional[float] = None  # best_fitness_index
    aggregate_strat: Optional[str] = None  # aggregation strategy
    config_group: Optional[str] = None  # config group
    best_scene: ConcreteScene = None    

    def save_to_json(self, path2=None):
        if self.path is None:
            if path2 is None:
                raise Exception('No path provided')
            with open(path2, "w") as file:
                json.dump(self.to_dict(), file, indent=4) 
        else:
            with open(self.path, 'w') as file:
                dict = self.to_dict()
                json.dump(dict, file, indent=4) 

    @classmethod
    def load_dict_from_json(cls, file_path: str) -> dict:
        with open(file_path, "r") as file:
            return json.load(file)
        
    @classmethod
    def load_from_json(cls, file_path: str) -> 'EvaluationData':
        return cls.from_dict(EvaluationData.load_dict_from_json(file_path))
        

    def __str__(self) -> str:
        return pprint.pformat(dict(sorted(self.to_dict().items())))
    
    def __repr__(self) -> str:
        return pprint.pformat(dict(sorted(self.to_dict().items())))
    
    def save_as_measurement(self):
        asset_folder = f'{ASSET_FOLDER}/gen_data/{self.measurement_name}/{self.config_group}/{self.algorithm_desc}'
        if not os.path.exists(asset_folder):
            os.makedirs(asset_folder)
        file_path=f"{asset_folder}/{self.scenario_name}_{self.timestamp.replace(':','-')}.json"
        self.path = file_path
        self.save_to_json()

    
    
