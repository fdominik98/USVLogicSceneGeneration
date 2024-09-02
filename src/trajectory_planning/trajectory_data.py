import json
from typing import Optional, List, Tuple, Dict

class TrajectoryData:
    def __init__(self, 
                 algorithm_desc: Optional[str] = None,
                 env_path: Optional[str] = None,
                 config_name: Optional[str] = None,
                 random_seed: Optional[int] = None,
                 max_iter: Optional[int] = None,
                 goal_sample_rate: Optional[float] = None,
                 expand_distance: Optional[float] = None,
                 timestamp: Optional[str] = None,
                 measurement_name: Optional[str] = None,
                 path: Optional[str] = None,
                 iter_numbers: Optional[Dict[str, Tuple[float, float]]] = None,
                 error_message: Optional[str] = None,
                 rrt_evaluation_times: Optional[Dict[str, Tuple[float, float]]] = None,
                 overall_eval_time: Optional[float] = None,
                 trajectories: Optional[Dict[int, List[Tuple[float, float, float, float]]]] = None):
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
        self.iter_numbers = iter_numbers or {}
        self.error_message = error_message
        self.overall_eval_time = overall_eval_time
        self.trajectories = trajectories or {}
        self.rrt_evaluation_times = rrt_evaluation_times or {}

    def to_dict(self) -> dict:
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
            "iter_numbers": self.iter_numbers,
            "error_message": self.error_message,
            "overall_eval_time": self.overall_eval_time,
            "trajectories": self.trajectories,
            "rrt_evaluation_times" : self.rrt_evaluation_times
        }

    def save_to_json(self, file_path: str):
        with open(file_path, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=4)

    @classmethod
    def from_dict(cls, data: dict):
        trajectories = {int(k): v for k, v in data.get("trajectories", {}).items()}
        return cls(
            algorithm_desc=data.get("algorithm_desc"),
            env_path=data.get("env_path"),
            config_name=data.get("config_name"),
            random_seed=data.get("random_seed"),
            max_iter=data.get("max_iter"),
            goal_sample_rate=data.get("goal_sample_rate"),
            expand_distance=data.get("expand_distance"),
            timestamp=data.get("timestamp"),
            measurement_name=data.get("measurement_name"),
            path=data.get("path"),
            iter_numbers=data.get("iter_numbers", {}),
            error_message=data.get("error_message"),
            overall_eval_time=data.get("overall_eval_time"),
            trajectories=trajectories,
            rrt_evaluation_times=data.get("rrt_evaluation_times", {})
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
