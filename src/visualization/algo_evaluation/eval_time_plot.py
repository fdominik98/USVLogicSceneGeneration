from typing import Dict, List
import matplotlib.pyplot as plt
from model.environment.usv_config import *
from evolutionary_computation.evaluation_data import EvaluationData
from visualization.algo_evaluation.algo_eval_utils import algo_mapper, vessel_number_mapper, algo_colors
from visualization.my_plot import MyPlot

class EvalTimePlot(MyPlot):  
    def __init__(self, measurements : Dict[str, Dict[str, List[EvaluationData]]]): 
        self.measurements = measurements
        self.eval_times = {
            key: {subkey: [data.evaluation_time for data in sublist if data.best_fitness_index == 0.0] for subkey, sublist in subdict.items()}
            for key, subdict in measurements.items()
        }  
        self.measurement_labels = vessel_number_mapper(list(measurements.keys()))
        MyPlot.__init__(self)
        
    def create_fig(self):
        fig, axes = plt.subplots(1, len(self.eval_times), figsize=(12, 4), gridspec_kw={'width_ratios': [1]*len(self.eval_times)})
        self.fig : plt.Figure = fig
        self.axes : List[plt.Axes] = axes
        fig.subplots_adjust(wspace=0.5)

        for i, (measurement_name, algo_measurements) in enumerate(self.eval_times.items()):
            labels = algo_mapper(list(algo_measurements.keys()))
            data = list(algo_measurements.values())
            
            if isinstance(axes, np.ndarray):
                axi : plt.Axes = axes[i]
            else:
                axi : plt.Axes = axes     
            boxplot = axi.boxplot(data, tick_labels=labels, patch_artist=True)
            axi.set_title(self.measurement_labels[i])
            axi.set_ylabel('Evaluation Time (s)')
            axi.set_aspect('auto', adjustable='box')
            axi.set_xticklabels(labels, rotation=45, ha='right')
            # Set colors and border widths for each box
            for patch, color in zip(boxplot['boxes'], algo_colors):
                patch.set_facecolor(color)           # Set fill color
                patch.set_linewidth(1.5)               # Set border width
            
            for element in ['whiskers', 'caps', 'medians']:
                for comp in boxplot[element]:
                    comp.set_linewidth(1.5)
            
            axi.set_ylim(0, 60)


        fig.tight_layout()