import os
import pandas as pd
from model.usv_environment import USVEnvironment
from genetic_algorithms.evaluation_data import EvaluationData

class DataParser():
    def __init__(self, measurement_folder : str) -> None:
        files = self.get_all_file_paths(measurement_folder)
        self.data : dict = [EvaluationData.load_dict_from_json(file) for file in files]
        
        data_lists : list[list[float]] = []
        
        column_names = ['evaluation_time', 'population_size', 'number_of_generations', 'num_parents_mating', 'mutate_prob', 'crossover_prob', 'mutate_eta', 'crossover_eta', 'result']
        
        for data in self.data:
            measurement_data = []
            for column in column_names:
                if data['error_message'] != None:
                    continue
                if column != 'result':
                    measurement_data.append(data[column])
                else:
                    fitness = data['best_fitness']
                    result = USVEnvironment.euler_distance(fitness)
                    measurement_data.append(-result)
            data_lists.append(measurement_data)
            
        self.df = pd.DataFrame(data_lists, columns=column_names)
        print(self.df)
    

    def get_all_file_paths(self, directory):
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if '.json' in file:
                    file_paths.append(os.path.join(root, file))
        return file_paths
    