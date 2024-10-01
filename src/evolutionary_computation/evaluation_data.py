import json
import pprint
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
                 timeout: Optional[float] = None,
                 init_method: Optional[str] = None,
                 c_1: Optional[float] = None,  # cognitive coefficient
                 c_2: Optional[float] = None,  # social coefficient
                 w: Optional[float] = None,    # inertia weight
                 best_fitness_index: Optional[float] = None,  # Add best_fitness_index
                 aggregate_strat: Optional[str] = None):  # New attribute for aggregation strategy
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
        self.timeout = timeout
        self.init_method = init_method
        self.c_1 = c_1  # Initialize c_1 parameter
        self.c_2 = c_2  # Initialize c_2 parameter
        self.w = w      # Initialize w parameter
        self.best_fitness_index = best_fitness_index  # Initialize best_fitness_index
        self.aggregate_strat = aggregate_strat  # Initialize new aggregate_strat parameter

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
            "timeout": self.timeout,
            "init_method": self.init_method,
            "c_1": self.c_1,  # Include c_1 in the dictionary
            "c_2": self.c_2,  # Include c_2 in the dictionary
            "w": self.w,      # Include w in the dictionary
            "best_fitness_index": self.best_fitness_index,  # Include best_fitness_index in the dictionary
            "aggregate_strat": self.aggregate_strat  # Include aggregate_strat in the dictionary
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
            timeout=data.get("timeout"),
            init_method=data.get("init_method"),
            c_1=data.get("c_1"),  # Extract c_1 from the dictionary
            c_2=data.get("c_2"),  # Extract c_2 from the dictionary
            w=data.get("w"),      # Extract w from the dictionary
            best_fitness_index=data.get("best_fitness_index"),  # Extract best_fitness_index from the dictionary
            aggregate_strat=data.get("aggregate_strat")  # Extract aggregate_strat from the dictionary
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
        return pprint.pformat(dict(sorted(self.to_dict().items())))
    
    def __repr__(self) -> str:
        return pprint.pformat(dict(sorted(self.to_dict().items())))
