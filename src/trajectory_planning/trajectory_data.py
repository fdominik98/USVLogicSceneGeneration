import json
from typing import Optional, List, Tuple

class TrajectoryData:
    def __init__(self, 
                 algorithm_desc: str,
                 env_path: str,
                 config_name: str,
                 random_seed: int,
                 max_iter: int,
                 goal_sample_rate: float,
                 expand_distance: float,
                 timestamp: str,
                 measurement_name: str,
                 path: str,
                 iter_number: Optional[int] = None,  # Can exceed max_iter
                 error_message: Optional[str] = None,
                 evaluation_time: Optional[float] = None,
                 trajectories: Optional[List[Tuple[float, float, float, float]]] = None):
        self.algorithm_desc = algorithm_desc
        self.env_path = env_path
        self.config_name = config_name
        self.random_seed = random_seed
        self.max_iter = max_iter
        self.goal_sample_rate = goal_sample_rate
        self.expand_distance = expand_distance
        self.timestamp = timestamp
        self.measurement_name = measurement_name
        self.path = path
        self.iter_number = iter_number
        self.error_message = error_message
        self.evaluation_time = evaluation_time
        self.trajectories = trajectories or []

    def to_dict(self):
        return {
            "algorithm_desc": self.algorithm_desc,
            "env_path": self.env_path,
            "config_name": self.config_name,
            "random_seed": self.random_seed,
            "max_iter": self.max_iter,
            "goal_sample_rate": self.goal_sample_rate,
            "expand_distance": self.expand_distance,
            "timestamp": self.timestamp,
            "measurement_name": self.measurement_name,
            "path": self.path,
            "iter_number": self.iter_number,
            "error_message": self.error_message,
            "evaluation_time": self.evaluation_time,
            "trajectories": self.trajectories,
        }

    def save_to_json(self, file_path: str):
        with open(file_path, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=4)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            algorithm_desc=data["algorithm_desc"],
            env_path=data["env_path"],
            config_name=data["config_name"],
            random_seed=data["random_seed"],
            max_iter=data["max_iter"],
            goal_sample_rate=data["goal_sample_rate"],
            expand_distance=data["expand_distance"],
            timestamp=data["timestamp"],
            measurement_name=data["measurement_name"],
            path=data["path"],
            iter_number=data.get("iter_number"),
            error_message=data.get("error_message"),
            evaluation_time=data.get("evaluation_time"),
            trajectories=data.get("trajectories", [])
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
