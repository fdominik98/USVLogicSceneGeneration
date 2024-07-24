import json
import traceback
from typing import Optional
from datetime import datetime

class EvaluationData:
    def __init__(self, algorithm_desc: str,
                 config_name: str,
                 random_seed: int,
                 evaluation_time: Optional[float] = None,
                 number_of_generations: Optional[int] = None,
                 actual_number_of_generations: Optional[int] = None,
                 population_size: Optional[int] = None,
                 num_parents_mating: Optional[int] = None,
                 best_solution: Optional[list[float]] = None,
                 best_fitness: Optional[list[float]] = None,
                 mutate_eta: Optional[float] = None,
                 mutate_prob: Optional[float] = None,
                 crossover_eta: Optional[float] = None,
                 crossover_prob: Optional[float] = None,
                 error_message: Optional[str] = None,
                 timestamp: Optional[str] = None):
        self.algorithm_desc = algorithm_desc
        self.config_name = config_name
        self.random_seed = random_seed
        self.evaluation_time = evaluation_time
        self.number_of_generations = number_of_generations
        self.actual_number_of_generations = actual_number_of_generations
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

    def to_dict(self):
        return {
            "algorithm_desc": self.algorithm_desc,
            "config_name": self.config_name,
            "random_seed": self.random_seed,
            "evaluation_time": self.evaluation_time,
            "number_of_generations": self.number_of_generations,
            "actual_number_of_generations": self.actual_number_of_generations,
            "population_size": self.population_size,
            "num_parents_mating": self.num_parents_mating,
            "best_solution": self.best_solution,
            "best_fitness": self.best_fitness,
            "mutate_eta": self.mutate_eta,
            "mutate_prob": self.mutate_prob,
            "crossover_eta": self.crossover_eta,
            "crossover_prob": self.crossover_prob,
            "error_message": self.error_message,
            "timestamp": self.timestamp
        }

    def save_to_json(self, file_path: str):
        with open(file_path, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=4)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            algorithm_desc=data["algorithm_desc"],
            config_name=data["config_name"],
            random_seed=data["random_seed"],
            evaluation_time=data.get("evaluation_time"),
            number_of_generations=data.get("number_of_generations"),
            actual_number_of_generations=data.get("actual_number_of_generations"),
            population_size=data.get("population_size"),
            num_parents_mating=data.get("num_parents_mating"),
            best_solution=data.get("best_solution"),
            best_fitness=data.get("best_fitness"),
            mutate_eta=data.get("mutate_eta"),
            mutate_prob=data.get("mutate_prob"),
            crossover_eta=data.get("crossover_eta"),
            crossover_prob=data.get("crossover_prob"),
            error_message=data.get("error_message"),
            timestamp=data.get("timestamp")
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