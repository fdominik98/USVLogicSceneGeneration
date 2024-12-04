from dataclasses import asdict, dataclass
import pprint
from typing import Optional, Dict
import jsonpickle
from concrete_level.models.trajectories import Trajectories

@dataclass
class TrajectoryData:
    algorithm_desc: Optional[str] = None
    env_path: Optional[str] = None
    config_name: Optional[str] = None
    random_seed: Optional[int] = None
    max_iter: Optional[int] = None
    goal_sample_rate: Optional[float] = None
    expand_distances: Optional[Dict[int, float]] = None
    timestamp: Optional[str] = None
    measurement_name: Optional[str] = None
    path: Optional[str] = None
    iter_numbers: Optional[Dict[int, int]] = None
    error_message: Optional[str] = None
    rrt_evaluation_times: Optional[Dict[int, float]] = None
    overall_eval_time: Optional[float] = None
    trajectories: Optional[Trajectories] = None

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
        return asdict(cls.load_from_json(file_path))

    def __str__(self) -> str:
        return pprint.pformat(dict(sorted(asdict(self).items())))
    
    def __repr__(self) -> str:
        return pprint.pformat(dict(sorted(asdict(self).items())))
