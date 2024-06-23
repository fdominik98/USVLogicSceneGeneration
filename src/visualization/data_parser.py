import os
from genetic_algorithms.evaluation_data import EvaluationData
import pandas as pd

class DataParser():
    def __init__(self, measurement_folder : str) -> None:
        files = self.get_all_file_paths(measurement_folder)
        self.data : EvaluationData = [EvaluationData.load_from_json(file) for file in files]
        
        data_lists : list[list[float]] = []
        
    

    def get_all_file_paths(self, directory):
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if '.json' in file:
                    file_paths.append(os.path.join(root, file))
        return file_paths