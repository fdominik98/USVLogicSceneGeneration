import os
import pandas as pd
from model.usv_environment import USVEnvironment
from genetic_algorithms.evaluation_data import EvaluationData
import tkfilebrowser
class DataParser():
    script_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(script_path)
    assets_dir = f'{current_dir}/../../assets'
    
    def __init__(self) -> None:
    
        self.dfs : list[pd.DataFrame] = []    
        self.df_names : list[str] = []
        for dir in tkfilebrowser.askopendirnames(initialdir=self.assets_dir):
        
            files = self.get_all_file_paths(dir)
                
            self.data : list[dict] = [EvaluationData.load_dict_from_json(file) for file in files]
            data_lists : list[list[float]] = []
            
            column_names = ['best_solution', 'config_name', 'evaluation_time', 'population_size', 'actual_number_of_generations', 'num_parents_mating', 'mutate_prob', 'crossover_prob', 'mutate_eta', 'crossover_eta', 'result']
            
            for data in self.data:
                measurement_data = []
                for column in column_names:
                    if data['error_message'] != None and data['best_solution'] != None:
                        continue
                    if column != 'result':
                        measurement_data.append(data[column])
                    else:
                        fitness = data['best_fitness']
                        result = USVEnvironment.euler_distance(fitness)
                        measurement_data.append(-result)
                data_lists.append(measurement_data)
                
            self.dfs.append(pd.DataFrame(data_lists, columns=column_names))
            self.df_names.append(f'{os.path.basename(dir).split(" - ")[0]}\n{data["config_name"]}')

    def get_all_file_paths(self, directory):
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if '.json' in file:
                    file_paths.append(os.path.join(root, file))
        return file_paths
    