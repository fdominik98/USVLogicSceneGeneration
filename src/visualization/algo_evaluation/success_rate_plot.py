from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from evolutionary_computation.evaluation_data import EvaluationData
from model.environment.usv_config import EPSILON
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, vessel_number_mapper, algo_colors
from visualization.my_plot import MyPlot

class SuccessRatePlot(MyPlot):  
    def __init__(self, measurements : Dict[str, Dict[str, List[EvaluationData]]]): 
        self.measurements = measurements
        self.success_rates = {
            key: {subkey: [0 if data.best_fitness_index >= EPSILON else 1 for data in sublist] for subkey, sublist in subdict.items()}
            for key, subdict in measurements.items()
        } 
        self.measurement_labels = vessel_number_mapper(list(measurements.keys()))
        MyPlot.__init__(self)
        
    def create_fig(self):
        fig, axes = plt.subplots(1, len(self.success_rates), figsize=(12, 4), gridspec_kw={'width_ratios': [1]*len(self.success_rates)})
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)

        for i, (measurement_name, algo_measurements) in enumerate(self.success_rates.items()):
            labels = algo_mapper(list(algo_measurements.keys()))
            percentages = [np.mean(data) * 100 for data in algo_measurements.values()]
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes  
            axi.bar(labels, percentages, color=algo_colors, edgecolor='black', linewidth=2)
            axi.set_title(self.measurement_labels[i])
            axi.set_ylabel('Success rate (%)')
            axi.set_aspect('auto', adjustable='box')
            axi.set_xticks(range(len(labels))) 
            axi.set_xticklabels(labels, rotation=45, ha='right')
            axi.set_ylim(0, 100)

        fig.tight_layout()