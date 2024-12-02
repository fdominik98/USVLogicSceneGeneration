from dataclasses import asdict, dataclass
import pprint
from typing import Optional, List
from concrete_level.model.concrete_scene import ConcreteScene
import jsonpickle

@dataclass()
class EvaluationData2:
    algorithm_desc: Optional[str] = None
    config_name: Optional[str] = None
    random_seed: Optional[int] = None
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
    best_scene: Optional[ConcreteScene] = None    

    def save_to_json(self, path2=None):
        json_str = jsonpickle.encode(self, indent=1)
        if self.path is None:
            if path2 is None:
                raise Exception('No path provided')
            with open(path2, "w") as file:
                file.write(json_str)
        else:
            with open(self.path, 'w') as file:
                file.write(json_str)

    @classmethod
    def load_from_json(cls, file_path: str):
        with open(file_path, "r") as file:
            json_str = file.read()
            return jsonpickle.decode(json_str)
        
    @classmethod
    def load_dict_from_json(cls, file_path: str) -> dict:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)

    def __str__(self) -> str:
        return pprint.pformat(dict(sorted(asdict(self).items())))
    
    def __repr__(self) -> str:
        return pprint.pformat(dict(sorted(asdict(self).items())))

    
    
