import os
import pandas as pd
from model.usv_environment import USVEnvironment
from genetic_algorithms.evaluation_data import EvaluationData
import tkfilebrowser
class DataParser():
    script_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(script_path)
    assets_dir = f'{current_dir}/../../assets'
    pymoo_dir = f'{assets_dir}/pymoo_algorithm'
    
    column_names = ['best_solution', 'config_name', 'measurement_name', 'evaluation_time', 'population_size', 'actual_number_of_generations', 'num_parents_mating', 'mutate_prob', 'crossover_prob', 'mutate_eta', 'crossover_eta', 'result']
    
    def __init__(self) -> None:
        pass

    def get_all_file_paths(self, directory):
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if '.json' in file:
                    file_paths.append(os.path.join(root, file))
        return file_paths
    
        
    def load_dirs(self) -> tuple[list[pd.DataFrame], list[str]]:
        dfs : list[pd.DataFrame] = []    
        df_names : list[str] = []
        for dir in tkfilebrowser.askopendirnames(initialdir=self.pymoo_dir):
            files = self.get_all_file_paths(dir)
            if len(files) == 0:
                continue
            df = self.load_data_from_files(files)
            df_name = f'{df["measurement_name"][0]}\n{df["config_name"][0]}'
            dfs.append(df)
            df_names.append(df_name)
        return dfs, df_names
    
    
    def load_files(self) -> tuple[pd.DataFrame, str]:
        files = tkfilebrowser.askopenfilenames(initialdir=self.pymoo_dir)
        df = self.load_data_from_files(files)
        if len(files) == 0:
            df_name = ''
        else:
            df_name = f'{df["measurement_name"][0]}\n{df["config_name"][0]}'
        return df, df_name
        
            
    def load_data_from_files(self, files : list[str]) -> pd.DataFrame:        
        data_lines : list[dict] = [EvaluationData.load_dict_from_json(file) for file in files]
        data_lists : list[list[float]] = []
        
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
    