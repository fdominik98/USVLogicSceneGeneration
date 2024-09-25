from abc import ABC, abstractmethod
import os
from typing import List, Tuple
import pandas as pd
from model.environment.usv_environment import USVEnvironment
from evolutionary_computation.evaluation_data import EvaluationData
import tkfilebrowser
from model.environment.usv_config import ASSET_FOLDER
from trajectory_planning.model.trajectory_data import TrajectoryData

class DataParser(ABC):
    gen_data_dir = f'{ASSET_FOLDER}/gen_data'
    RRT_DIR = f'{gen_data_dir}/RRTStar_algo'
    EVAL_DATA_COLUMN_NAMES = ['best_solution', 'config_name',
                              'measurement_name', 'evaluation_time',
                              'population_size', 'number_of_generations',
                              'num_parents_mating', 'mutate_prob', 'crossover_prob',
                              'mutate_eta', 'crossover_eta', 'path', 'result']
    
    TRAJ_COLUMN_NAMES = ['trajectories', 'config_name', 'measurement_name', 'rrt_evaluation_times',
                         'iter_numbers', 'overall_eval_time', 'path', 'env_path', 'expand_distance',
                         'goal_sample_rate', 'random_seed']
    
    
    def __init__(self, column_names : List[str], dir : str) -> None:
        self.column_names = column_names
        self.dir = dir
        
    @abstractmethod    
    def get_data_lines(self, files : List[str]) -> List[dict]:
        pass

    def get_all_file_paths(self, directory):
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if '.json' in file:
                    file_paths.append(os.path.join(root, file))
        return file_paths
    
        
    def load_dirs(self) -> Tuple[List[pd.DataFrame], List[str]]:
        dfs : List[pd.DataFrame] = []    
        df_names : List[str] = []
        for dir in tkfilebrowser.askopendirnames(initialdir=self.dir):
            files = self.get_all_file_paths(dir)
            if len(files) == 0:
                continue
            df = self.load_df_from_files(files)
            df_name = f'{df["measurement_name"][0]}\n{df["config_name"][0]}'
            dfs.append(df)
            df_names.append(df_name)
        return dfs, df_names
    
    
    def load_df(self) -> Tuple[pd.DataFrame, str]:
        files = tkfilebrowser.askopenfilenames(initialdir=self.dir)
        df = self.load_df_from_files(files)
        if len(files) == 0:
            df_name = ''
        else:
            df_name = f'{df["measurement_name"][0]}\n{df["config_name"][0]}'
        return df, df_name
        
            
    def load_df_from_files(self, files : List[str]) -> pd.DataFrame:        
        data_lines = self.get_data_lines(files)
        data_lists : List[List[float]] = []
        
        for data in data_lines:
            measurement_data = []
            for column in self.column_names:
                if data['error_message'] != None and data['best_solution'] != None:
                    continue
                if column != 'result':
                    measurement_data.append(data[column])
                else:
                    fitness = data['best_fitness']
                    result = USVEnvironment.euler_distance(fitness)
                    measurement_data.append(-result)
            data_lists.append(measurement_data)
            
        return pd.DataFrame(data_lists, columns=self.column_names)

class EvalDataParser(DataParser):    
    def __init__(self) -> None:
        super().__init__(self.EVAL_DATA_COLUMN_NAMES, self.gen_data_dir)

    
    def get_data_lines(self, files : List[str]) -> List[dict]:
        return [EvaluationData.load_dict_from_json(file) for file in files]
    
    def load_data_models(self) -> List[EvaluationData]:
        files = tkfilebrowser.askopenfilenames(initialdir=self.dir)
        return self.load_data_models_from_files(files)
    
    def load_data_models_from_files(self, files : List[str]) -> List[EvaluationData]:
        return [EvaluationData.load_from_json(file) for file in files]
    
class TrajDataParser(DataParser):    
    def __init__(self) -> None:
        super().__init__(self.TRAJ_COLUMN_NAMES, self.RRT_DIR)

    
    def get_data_lines(self, files : List[str]) -> List[dict]:
        return [TrajectoryData.load_dict_from_json(file) for file in files]
    
    def load_data_models(self) -> List[TrajectoryData]:
        files = tkfilebrowser.askopenfilenames(initialdir=self.dir)
        return self.load_data_models_from_files(files)
    
    def load_data_models_from_files(self, files : List[str]) -> List[TrajectoryData]:
        return [TrajectoryData.load_from_json(file) for file in files]
    