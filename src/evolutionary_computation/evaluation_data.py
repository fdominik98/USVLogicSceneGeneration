import json
from typing import Optional, List

class EvaluationData:
    def __init__(self, 
                 algorithm_desc: Optional[str] = None,
                 config_name: Optional[str] = None,
                 random_seed: Optional[int] = None,
                 evaluation_time: Optional[float] = None,
                 number_of_generations: Optional[int] = None,
                 population_size: Optional[int] = None,
                 num_parents_mating: Optional[int] = None,
                 best_solution: Optional[List[float]] = None,
                 best_fitness: Optional[List[float]] = None,
                 mutate_eta: Optional[float] = None,
                 mutate_prob: Optional[float] = None,
                 crossover_eta: Optional[float] = None,
                 crossover_prob: Optional[float] = None,
                 error_message: Optional[str] = None,
                 timestamp: Optional[str] = None,
                 measurement_name: Optional[str] = None,
                 path: Optional[str] = None,
                 timeout: Optional[float] = None,  # Added timeout parameter
                 random_init: Optional[bool] = None):  # Added random_init parameter
        self.algorithm_desc = algorithm_desc
        self.config_name = config_name
        self.random_seed = random_seed
        self.evaluation_time = evaluation_time
        self.number_of_generations = number_of_generations
        self.population_size = population_size
        self.num_parents_mating = num_parents_mating
        self.best_solution = best_solution
        self.best_fitness = best_fitness
        self.mutate_eta = mutate_eta
        self.mutate_prob = mutate_prob
        self.crossover_eta = crossover_eta
        self.crossover_prob = crossover_prob
        self.error_message = error_message
        self.timestamp = timestamp
        self.measurement_name = measurement_name
        self.path = path
        self.timeout = timeout  # Initialize timeout parameter
        self.random_init = random_init  # Initialize random_init parameter

    def to_dict(self):
        return {
            "algorithm_desc": self.algorithm_desc,
            "config_name": self.config_name,
            "random_seed": self.random_seed,
            "evaluation_time": self.evaluation_time,
            "number_of_generations": self.number_of_generations,
            "population_size": self.population_size,
            "num_parents_mating": self.num_parents_mating,
            "best_solution": self.best_solution,
            "best_fitness": self.best_fitness,
            "mutate_eta": self.mutate_eta,
            "mutate_prob": self.mutate_prob,
            "crossover_eta": self.crossover_eta,
            "crossover_prob": self.crossover_prob,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
            "measurement_name": self.measurement_name,
            "path": self.path,
            "timeout": self.timeout,  # Include timeout in the dictionary
            "random_init": self.random_init  # Include random_init in the dictionary
        }

    def save_to_json(self, file_path: str):
        with open(file_path, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=4)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            algorithm_desc=data.get("algorithm_desc"),
            config_name=data.get("config_name"),
            random_seed=data.get("random_seed"),
            evaluation_time=data.get("evaluation_time"),
            number_of_generations=data.get("number_of_generations"),
            population_size=data.get("population_size"),
            num_parents_mating=data.get("num_parents_mating"),
            best_solution=data.get("best_solution"),
            best_fitness=data.get("best_fitness"),
            mutate_eta=data.get("mutate_eta"),
            mutate_prob=data.get("mutate_prob"),
            crossover_eta=data.get("crossover_eta"),
            crossover_prob=data.get("crossover_prob"),
            error_message=data.get("error_message"),
            timestamp=data.get("timestamp"),
            measurement_name=data.get("measurement_name"),
            path=data.get("path"),
            timeout=data.get("timeout"),  # Extract timeout from the dictionary
            random_init=data.get("random_init")  # Extract random_init from the dictionary
        )
        
    @classmethod
    def load_from_json(cls, file_path: str):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return cls.from_dict(data)
        
    @classmethod
    def load_dict_from_json(cls, file_path: str) -> dict:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)

    def __str__(self) -> str:
        return str(self.to_dict())
