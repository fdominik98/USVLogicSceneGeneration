from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import List, Tuple
import pandas as pd
from logical_level.constraint_satisfaction.evolutionary_computation.evaluation_data import EvaluationData
import tkfilebrowser
from utils.file_system_utils import ASSET_FOLDER, get_all_file_paths
from concrete_level.trajectory_generation.trajectory_data import TrajectoryData

class DataParser(ABC):
    gen_data_dir = f'{ASSET_FOLDER}/gen_data'
    RRT_DIR = f'{gen_data_dir}/RRTStar_algo'
    EVAL_DATA_COLUMN_NAMES = list(sorted(asdict(EvaluationData()).keys()))
    
    TRAJ_COLUMN_NAMES = ['trajectories', 'config_name', 'measurement_name', 'rrt_evaluation_times',
                         'iter_numbers', 'overall_eval_time', 'path', 'env_path', 'expand_distance',
                         'goal_sample_rate', 'random_seed']
    
    
    def __init__(self, column_names : List[str], dir : str) -> None:
        self.column_names = column_names
        self.dir = dir
        
    def get_data_lines(self, files : List[str]) -> List[dict]:
        return [self.load_dict_from_file(file) for file in files]
    
    @abstractmethod
    def load_dict_from_file(self, file : str) -> dict:
        pass
         
    def load_df_from_files(self, files : List[str]) -> pd.DataFrame:        
        data_lines = self.get_data_lines(files)
        data_lists : List[List[float]] = []
        
        for data in data_lines:
            measurement_data = []
            if data['error_message'] != None and data['best_solution'] != None:
                continue
            for column in self.column_names:
                measurement_data.append(data[column])
            data_lists.append(measurement_data)
            
        return pd.DataFrame(data_lists, columns=self.column_names)
    
    def load_dirs_merged(self, dirs=[]) -> Tuple[pd.DataFrame, List[str]]:
        files = []
        if len(dirs) == 0:
            dirs = tkfilebrowser.askopendirnames(initialdir=self.dir)
        for dir in dirs:
            files += get_all_file_paths(dir, 'json')
            if len(files) == 0:
                continue
        return self.load_df_from_files(files), dirs
    

class EvalDataParser(DataParser):    
    def __init__(self) -> None:
        super().__init__(self.EVAL_DATA_COLUMN_NAMES, self.gen_data_dir)

    def load_data_models(self) -> List[EvaluationData]:
        files = tkfilebrowser.askopenfilenames(initialdir=self.dir)
        return self.load_data_models_from_files(files)
    
    def load_data_models_from_files(self, files : List[str]) -> List[EvaluationData]:
        data_models = [self.load_model_from_file(file) for file in files]
        return [model for model in data_models if model.error_message is None and model.best_scene is not None]
    
    def load_dirs_merged_as_models(self) -> List[EvaluationData]:
        files = []
        for dir in tkfilebrowser.askopendirnames(initialdir=self.dir):
            files += get_all_file_paths(dir, 'json')
            if len(files) == 0:
                continue
        return self.load_data_models_from_files(files)
    
    def load_dict_from_file(self, file : str) -> dict:
        dict = EvaluationData.load_dict_from_json(file)
        dict['path'] = file
        return dict
    
    def load_model_from_file(self, file : str) -> EvaluationData:
        model : EvaluationData = EvaluationData.load_from_json(file)
        model.path = file
        return model
    
class TrajDataParser(DataParser):    
    def __init__(self) -> None:
        super().__init__(self.TRAJ_COLUMN_NAMES, self.RRT_DIR)

    def load_data_models(self) -> List[TrajectoryData]:
        files = tkfilebrowser.askopenfilenames(initialdir=self.dir)
        return self.load_models_from_files(files)
    
    def load_models_from_files(self, files : List[str]) -> List[TrajectoryData]:
        data_models = [self.load_model_from_file(file) for file in files]
        return [model for model in data_models if model.error_message is None and model.trajectories is not None]
    
    def load_dict_from_file(self, file : str) -> dict:
        dict = TrajectoryData.load_dict_from_json(file)
        dict['path'] = file
        return dict
    
    def load_model_from_file(self, file : str) -> TrajectoryData:
        model : EvaluationData = TrajectoryData.load_from_json(file)
        model.path = file
        return model